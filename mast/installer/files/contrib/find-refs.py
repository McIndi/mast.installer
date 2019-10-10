import os
import json
from lxml import etree
from collections import defaultdict
from mast.logging import make_logger
import mast.datapower.datapower as datapower
from mast import __version__
from mast.cli import Cli
from itertools import islice, cycle

def splice(right, left):
    return islice(
        list(zip(
            cycle(right),
            cycle(left),
        )),
        0,
        max(
            len(right),
            len(left),
        )
    )

def tree():
    return defaultdict(tree)

def main(appliances=[],
         credentials=[],
         timeout=120,
         no_check_hostname=False,
         domains=[],
         out_file="tmp/cert-audit.json",
         object_classes=[],
         object_names=[]
     ):
    logger = make_logger("find_refs")
    if out_file is None:
        logger.error("Must specify out file")
        sys.exit(2)
    if not os.path.exists(os.path.dirname(out_file)):
        os.makedirs(os.path.dirname(out_file))
    check_hostname = not no_check_hostname
    env = datapower.Environment(
        appliances,
        credentials,
        timeout,
        check_hostname=check_hostname)

    out = tree()
    for appliance in env.appliances:
        hostname = appliance.hostname
        print(hostname)
        logger.info("Checking appliance {}".format(appliance.hostname))
        _domains = domains
        if "all-domains" in domains:
            _domains = appliance.domains
        for domain in _domains:
            print(("\t{}".format(domain)))
            logger.info("In domain {}".format(domain))
            config = etree.fromstring(str(appliance.get_config(domain=domain)))
            for object_class, object_name in splice(object_classes, object_names):
                obj = config.xpath(".//{}[@name='{}']".format(object_class, object_name))
                if not obj:
                    print(("\t\t{}: {} Not Found".format(object_class, object_name)))
                    continue
                print(("\t\t{}: {}".format(object_class, object_name)))
                node = out[hostname][domain]["{}: {}".format(object_class, object_name)]
                recurse_config(config, object_class, object_name, node)
    with open(out_file, "wb") as fp:
        json.dump(out, fp, indent=4)

def recurse_config(config, object_class, object_name, node, level=1):
    for match in config.xpath(".//*[local-name()='config']/*[.//*/@class='{}' and .//*/text()='{}']".format(object_class, object_name)):
        print(("{}{}: {}".format("\t"*(2+level), match.tag, match.get("name"))))
        klass, name = match.tag, match.get("name")
        _node = node["{}: {}".format(klass, name)]
        recurse_config(config, klass, name, _node, level=level+1)

if __name__ == "__main__":
    cli = Cli(main=main)
    try:
        cli.run()
    except SystemExit:
        pass
    except:
        make_logger("error").exception("An unhandled exception has occurred")
        raise
