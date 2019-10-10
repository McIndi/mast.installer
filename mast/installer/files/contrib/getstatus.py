import os
import openpyxl
from time import sleep
from mast.cli import Cli
from mast.logging import make_logger
from mast.datapower import datapower
from mast.timestamp import Timestamp
from mast.datapower.datapower import Environment

t = Timestamp()

logger = make_logger("mast.getstatus", propagate=False)


def recurse_status(prefix, elem, row, header_row):
    for child in elem.findall(".//*"):
        logger.info("Found child {}".format(child.tag))
        if child.tag not in header_row:
            logger.debug("Appending {} to header row".format(child.tag))
            header_row.append(child.tag)
        if len(child):
            _prefix = "{}/{}".format(prefix, child.tag)
            logger.info("child {} has children, recursing...".format(_prefix))
            recurse_status(_prefix, child, row, header_row)
        else:
            logger.info("Adding {} -> {}".format(child.tag, child.text))
            row.insert(header_row.index(child.tag), child.text)


def create_workbook(
        env,       domains,
        providers, delay,
        out_file,  timestamp,
        prepend_timestamp):

    xpath = datapower.STATUS_XPATH
    wb = openpyxl.Workbook()
    base_header_row = ["timestamp", "hostname", "domain", "provider"]

    if prepend_timestamp:
        filename = os.path.split(out_file)[-1]
        filename = "{}-{}".format(t.timestamp, filename)
        path = list(os.path.split(out_file)[:-1])
        path.append(filename)
        out_file = os.path.join(*path)

    logger.info("Generating Workbook - will be stored in {}".format(out_file))
    skip = []
    for provider in providers:
        sheet = wb.create_sheet(title=provider[:31])
        header_row = list(base_header_row)
        rows = []
        for appliance in env.appliances:
            if appliance in skip:
                continue
            print(("checking {}".format(provider)))
            logger.info("Checking Status Provider {}".format(provider))
            print(("\t{}".format(appliance.hostname)))
            try:
                if "all-domains" in domains:
                    _domains = appliance.domains
                else:
                    _domains = domains
            except:
                print((" ".join((
                    "ERROR: See log for details,",
                    "skipping appliance {}".format(appliance.hostname)
                ))))
                logger.exception(
                    "An unhandled exception was raised while "
                    "retrieving list of domains."
                    "Skipping appliance {}.".format(appliance.hostname)
                )
                skip.append(appliance)
                continue
            for domain in _domains:
                print(("\t\t{}".format(domain)))
                sleep(delay)
                try:
                    logger.info(
                        "Querying {} for {} in domain {}".format(
                            appliance.hostname,
                            provider,
                            domain
                        )
                    )
                    response = appliance.get_status(provider, domain=domain)
                except datapower.AuthenticationFailure:
                    logger.warn(
                        "Recieved AuthenticationFailure. "
                        "Retrying in 5 seconds...")
                    print((" ".join((
                        "Recieved AuthenticationFailure.",
                        "Retrying in 5 seconds..."
                    ))))
                    sleep(5)
                    try:
                        response = appliance.get_status(
                            provider,
                            domain=domain
                        )
                    except datapower.AuthenticationFailure:
                        print("Received AuthenticationFailure again. Skipping.")
                        logger.error(
                            "Received AuthenticationFailure again. Skipping."
                        )
                        skip.append(appliance)
                        continue
                except:
                    print((" ".join((
                        "ERROR: See log for details,",
                        "skipping appliance {}".format(appliance.hostname)
                    ))))
                    logger.exception(
                        "An unhandled exception was raised. "
                        "Skipping appliance {}.".format(appliance.hostname)
                    )
                    skip.append(appliance)
                    break
                timestamp = response.xml.find(datapower.BASE_XPATH).text
                for node in response.xml.findall(xpath):
                    row = [timestamp, appliance.hostname, domain, provider]
                    recurse_status("", node, row, header_row)
                    rows.append(row)
        sheet.append(header_row)
        for row in rows:
            sheet.append(row)

    Sheet = wb.get_sheet_by_name("Sheet")
    wb.remove_sheet(Sheet)
    logger.info("Writing workbook {}".format(out_file))
    wb.save(out_file)


def main(appliances=[],
         credentials=[],
         timeout=120,
         no_check_hostname=False,
         domains=["default"],
         providers=[],
         delay=0.5,
         out_file="./status.xlsx",
         by_appliance=False,
         no_prepend_timestamp=False):

    prepend_timestamp = not no_prepend_timestamp
    t = Timestamp()

    check_hostname = not no_check_hostname
    if by_appliance:
        logger.info("Generating workbooks by appliance")
        # we make the initial Environment to correctly handle credentials
        env = Environment(
            appliances,
            credentials,
            timeout,
            check_hostname=check_hostname
        )
        for appliance in env.appliances:
            logger.info(
                "generating workbook for {}".format(appliance.hostname)
            )
            filename = os.path.split(out_file)[-1]
            filename = "{}-{}".format(appliance.hostname, filename)
            path = list(os.path.split(out_file)[:-1])
            path.append(filename)
            _out_file = os.path.join(*path)
            logger.info(
                "Workbook for {} will be stored in {}".format(
                    appliance.hostname, _out_file
                )
            )
            _env = Environment(
                [appliance.hostname],
                [appliance.credentials],
                timeout,
                check_hostname)
            create_workbook(
                _env,
                domains,
                providers,
                delay,
                _out_file,
                t,
                prepend_timestamp
            )
    else:
        logger.info("generating workbook")
        env = Environment(
            appliances,
            credentials,
            timeout,
            check_hostname=False
        )
        create_workbook(
            env,
            domains,
            providers,
            delay,
            out_file,
            t,
            prepend_timestamp
        )


if __name__ == "__main__":
    try:
        cli = Cli(main=main)
        cli.run()
    except:
        logger.exception("An unhandled exception occured during execution.")
        raise
