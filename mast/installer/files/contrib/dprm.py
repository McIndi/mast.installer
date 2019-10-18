"""Remove files from DataPower using glob patterns
"""

from mast.datapower import datapower
from mast.logging import make_logger
from mast.pprint import pprint_xml_str, pprint_xml
from collections import defaultdict
from mast.cli import Cli
from fnmatch import fnmatch
from lxml import etree
import os
import re

def main(appliances=[],
         credentials=[],
         timeout=120,
         no_check_hostname=False,
         domains=[],
         paths=[],
         force=False,
         dry_run=False):
    check_hostname = not no_check_hostname
    env = datapower.Environment(appliances,
                                credentials,
                                timeout=timeout,
                                check_hostname=check_hostname)
    for appliance in env.appliances:
        _domains = domains
        if "all-domains" in _domains:
            _domains = appliance.domains
        print((appliance.hostname))
        for domain in domains:
            print(("\t{}".format(domain)))
            filestore_dict = defaultdict(list)
            for path in paths:
                location = path.split(":")[0] + ":"
                if location not in filestore_dict:
                    filestore = appliance.get_filestore(domain, location)
                    filestore_dict[location] = filestore.xml
                for directory in filestore_dict[location].xpath(".//directory"):
                    # print(directory.get("name"))
                    if fnmatch(directory.get("name"), path):
                        print(("\t\t{}".format(directory.get("name"))))
                        if len(directory) and not force:
                            print("\t\t\tDirectory not empty, use `--force` to remove this directory")
                            continue
                        if dry_run:
                            continue
                        resp = appliance.RemoveDir(
                            domain=domain,
                            Dir=directory.get("name"),
                        )
                        resp = etree.fromstring(resp.text)
                        msg = " ".join(resp.itertext())
                        print(("\t\t\t{}".format(msg)))
                        continue
                    for node in directory.xpath("./file"):
                        name = "/".join((node.getparent().get("name"), node.get("name")))
                        if fnmatch(name, path):
                            print(("\t\t{}".format(name)))
                            if dry_run:
                                continue
                            resp = appliance.DeleteFile(
                                domain=domain,
                                File=name
                            )
                            resp = resp.xml
                            msg = " ".join(resp.itertext())
                            print(("\t\t\t{}".format(msg)))
if __name__ == "__main__":
    cli = Cli(main=main, description=__doc__)
    try:
        cli.run()
    except SystemExit:
        pass
    except:
        make_logger("error").exception("An unhandled exception occurred")
        raise
