import os
from pprint import pprint
from openpyxl import Workbook
import datapower
from datapower import DataPower, CONFIG_XPATH, Environment
import logging
from cli import Cli
from timestamp import Timestamp

t = Timestamp()
logging.basicConfig(
    filename="{}-getconfig.log".format(t.timestamp),
    filemode="w",
    format="level=%(levelname)s; datetime=%(asctime)s; process_name=%(processName)s; pid=%(process)d; thread=%(thread)d; module=%(module)s; function=%(funcName)s; line=%(lineno)d; message=%(message)s")
logger = logging.getLogger("getconfig")
logger.setLevel(10)

def add_to_header(column_name, header_row):
    if column_name in header_row:
        pass
    else:
        header_row.append(column_name)

def _recurse_config(prefix, node, row, header_row, delim):
    if list(node):
        for child in list(node):
            new_prefix = "{}/{}".format(prefix, child.tag)
            logger.info("Found child node {}".format(new_prefix))
            _recurse_config(new_prefix, child, row, header_row, delim)
        for attr in node.keys():
            value = node.get(attr).strip() or "N/A"
            field_name = "{}[@{}]".format(prefix, attr)
            logger.info("Found attribute {} - {}".format(field_name, value))
            add_to_header(field_name, header_row)
            row[header_row.index(field_name)] = value
    else:
        logger.info("No child nodes found")
        if not node.text:
            node.text = "N/A"
        add_to_header(prefix, header_row)
        index = header_row.index(prefix)
        if not row[index]:
            logger.info("Found value for {} -> {}".format(node.tag, node.text))
            row[index] = node.text
        else:
            logger.info("Found additional value for {} -> {}".format(node.tag, node.text))
            row[index] = "{}{}{}".format(row[index], delim, node.text)
        for attr in node.keys():
            value = node.get(attr).strip() or "N/A"
            field_name = "{}[@{}]".format(prefix, attr)
            logger.info("Found attribute {} -> {}".format(field_name, value))
            add_to_header(field_name, header_row)
            row[header_row.index(field_name)] = value

def create_workbook(env, object_classes, domains, out_file,
                    delim):
    wb = Workbook()
    logger.info("Querying for configuration")
    skip = []
    for object_class in object_classes:
        header_row = ["appliance", "domain", "Object Class", "Object Name"]
        rows = []
        ws = wb.create_sheet(title=object_class)
        for dp in env.appliances:
            if dp in skip:
                continue
            print "Retrieving {}".format(object_class)
            logger.info("Retrieving {} configuration".format(object_class))
            print "\t{}".format(dp.hostname)
            logger.info("Querying {}".format(dp.hostname))
            _domains = domains
            if "all-domains" in domains:
                try:
                    _domains = dp.domains
                except:
                    print "ERROR: See log for details, skipping appliance {}".format(dp.hostname)
                    logger.exception("An unhandled exception was raised while retrieving list of domains. Skipping appliance {}.".format(dp.hostname))
                    skip.append(dp)
                    continue
            for domain in _domains:
                print "\t\t{}".format(domain)
                logger.info("Looking in domain {}".format(domain))
                xpath = CONFIG_XPATH + object_class
                try:
                    logger.info("Querying {} for {} in domain {}".format(dp.hostname, object_class, domain))
                    config = dp.get_config(_class=object_class, domain=domain)
                except datapower.AuthenticationFailure:
                    logger.warn("Recieved AuthenticationFailure. Retrying in 5 seconds...")
                    print "Recieved AuthenticationFailure. Retrying in 5 seconds..."
                    sleep(5)
                    try:
                        config = dp.get_config(_class=object_class, domain=domain)
                    except dataPower.AuthenticationFailure:
                        print "Received AuthenticationFailure again. Skipping."
                        logger.error("Received AuthenticationFailure again. Skipping.")
                        skip.append(dp)
                        continue
                except:
                    print "ERROR: See log for details, skipping appliance {}".format(dp.hostname)
                    logger.exception("An unhandled exception was raised. Skipping appliance {}.".format(dp.hostname))
                    skip.append(dp)
                    break                
                nodes = config.xml.findall(xpath)
                for index, node in enumerate(nodes):
                    name = node.get("name")
                    logger.info("Found node {} - {}".format(node.tag, name))
                    row = [dp.hostname, domain, object_class, name]
                    row.extend([None] * 1500)
                    for child in list(node):
                        logger.info("Found child node {}. recursing...".format(child))
                        _recurse_config(child.tag, child, row, header_row, delim)
                    rows.append(row)
        rows.insert(0, header_row)
        for row in rows:
            ws.append(row)

    wb.remove_sheet(wb.worksheets[0])

    logger.info("writing workbook {}".format(out_file))
    wb.save(out_file)


def main(appliances=[], credentials=[], object_classes=[], domains=[], timeout=120, no_check_hostname=False,
        out_file="sample.xlsx", delim=os.linesep, by_appliance=False):
    
    check_hostname = not no_check_hostname
    if by_appliance:
        logger.info("Generating workbooks by appliance")
        # we make the initial Environment to correctly handle credentials
        env = Environment(appliances, credentials, timeout, check_hostname=check_hostname)
        for appliance in env.appliances:
            logger.info("generating workbook for {}".format(appliance.hostname))
            filename = os.path.split(out_file)[-1]
            filename = "{}-{}".format(appliance.hostname, filename)
            path = list(os.path.split(out_file)[:-1])
            path.append(filename)
            _out_file = os.path.join(*path)
            logger.info(
                "Workbook for {} will be stored in {}".format(
                    appliance.hostname, _out_file))
            _env = Environment(
                [appliance.hostname],
                [appliance.credentials],
                timeout,
                check_hostname)
            create_workbook(_env, object_classes, domains, _out_file, delim)        
    else:
        logger.info("generating workbook")
        env = Environment(appliances, credentials, timeout, check_hostname=check_hostname)
        create_workbook(env, object_classes, domains, out_file, delim)
        

if __name__ == "__main__":
    try:
        cli = Cli(main=main)
        cli.run()
    except:
        logger.exception("An unhandled exception occured during execution.")
        raise

