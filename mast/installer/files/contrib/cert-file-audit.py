# -*- coding: utf-8 -*-
import os
import openpyxl
from mast.cli import Cli
from mast.logging import make_logger
from mast.datapower import datapower
from mast.timestamp import Timestamp
import xml.etree.cElementTree as etree

logger = make_logger("mast.cert-file-audit")

default_out_file = os.path.join("tmp", "cert-file-audit.xlsx")
def main(appliances=[],
         credentials=[],
         timeout=120,
         no_check_hostname=False,
         out_file=default_out_file):
    locations = ["cert:", "pubcert:", "sharedcert:"]
    check_hostname = not no_check_hostname
    env = datapower.Environment(appliances,
                                credentials,
                                timeout,
                                check_hostname=check_hostname)

    header_row = ["appliance",
                  "domain",
                  "directory",
                  "filename",
                  "size",
                  "modified"]
    rows = []

    for appliance in env.appliances:
        print appliance.hostname
        domain = "default"

        for location in locations:
            print "\t{}".format(location)
            filestore = appliance.get_filestore(domain=domain,
                                                location=location)
            _location = filestore.xml.find(datapower.FILESTORE_XPATH)
            if _location is None:
                continue
            if _location.findall("./file") is not None:
                for _file in _location.findall("./file"):
                    dir_name = _location.get("name")
                    filename = _file.get("name")
                    print "\t\t{}".format(filename)
                    size = _file.find("size").text
                    modified = _file.find("modified").text
                    rows.append([appliance.hostname,
                                 domain,
                                 dir_name,
                                 filename,
                                 size,
                                 modified])
            for directory in _location.findall(".//directory"):
                dir_name = directory.get("name")
                print "\t\t{}".format(dir_name)
                for _file in directory.findall(".//file"):
                    filename = _file.get("name")
                    print "\t\t\t{}".format(filename)
                    size = _file.find("size").text
                    modified = _file.find("modified").text

                    rows.append([appliance.hostname,
                                 domain,
                                 dir_name,
                                 filename,
                                 size,
                                 modified])
    wb = openpyxl.Workbook()
    ws = wb.get_active_sheet()
    ws.title = "CertFileAudit"
    ws.append(header_row)
    for row in rows:
        ws.append(row)
    wb.save(out_file)

if __name__ == "__main__":
    cli = Cli(main=main)
    try:
        cli.run()
    except SystemExit:
        pass
    except:
        logger.exception("An unhandled exception occured during execution.")
        raise

