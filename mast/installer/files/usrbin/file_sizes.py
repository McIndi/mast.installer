import logging
import datapower
from cli import Cli
from tstamp import Timestamp
import xml.etree.cElementTree as etree

t = Timestamp()
logging.basicConfig(
    filename="{}-file_sizes.log".format(t.timestamp),
    filemode="w",
    format="level=%(levelname)s; datetime=%(asctime)s; process_name=%(processName)s; pid=%(process)d; thread=%(thread)d; module=%(module)s; function=%(funcName)s; line=%(lineno)d; message=%(message)s")
logger = logging.getLogger("file_sizes")
logger.setLevel(10)


def main(appliances=[], credentials=[], timeout=120, no_check_hostname=False, out_file="out.csv"):
    locations = ["cert:", "chkpoints:", "config:", "export:", "image:", "local:", "logstore:", "logtemp:", "pubcert:", "sharedcert:", "store:", "tasktemplates:", "temporary:"]
    check_hostname = not no_check_hostname
    env = datapower.Environment(appliances, credentials, timeout, check_hostname=check_hostname)
    root_node = etree.fromstring("<filestores />")
    
    with open(out_file, "wb") as fout:
        fout.write("appliance,domain,directory,filename,size,modified\n")

    for appliance in env.appliances:
        print appliance.hostname
        appliance_node = etree.fromstring('<filestores appliance="{}" />'.format(appliance.hostname))
        for domain in appliance.domains:
            print "\t{}".format(domain)
            for location in locations:
                print "\t\t{}".format(location)
                filestore = appliance.get_filestore(domain=domain, location=location)
                _location = filestore.xml.find(datapower.FILESTORE_XPATH)
                if _location is None:
                    continue
                if _location.findall("./file") is not None:
                    for _file in _location.findall("./file"):
                        dir_name = _location.get("name")
                        filename = _file.get("name")
                        print "\t\t\t{}".format(filename)
                        size = _file.find("size").text
                        modified = _file.find("modified").text
                        with open(out_file, "ab") as fout:
                            fout.write("{},{},{},{},{},{}\n".format(appliance.hostname, domain, dir_name, filename, size, modified))
                for directory in _location.findall(".//directory"):
                    dir_name = directory.get("name")
                    print "\t\t\t{}".format(dir_name)
                    for _file in directory.findall(".//file"):
                        filename = _file.get("name")
                        print "\t\t\t\t{}".format(filename)
                        size = _file.find("size").text
                        modified = _file.find("modified").text
                        with open(out_file, "ab") as fout:
                            fout.write("{},{},{},{},{},{}\n".format(appliance.hostname, domain, dir_name, filename, size, modified))

if __name__ == "__main__":
    try:
        cli = Cli(main=main)
        cli.run()
    except:
        logger.exception("An unhandled exception occured during execution.")
        raise
