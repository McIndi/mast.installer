from mast.pprint import pprint, pprint_xml_str, pprint_xml
from mast.logging import make_logger
from mast.datapower import datapower
from lxml import etree
import mast.cli as cli
import os

__version__ = "{}-0".format(os.environ["MAST_VERSION"])

nsmap = {
    "env": "http://schemas.xmlsoap.org/soap/envelope/",
    "dp":"http://www.datapower.com/schemas/management"
}

def main(appliances=[],
         credentials=[],
         timeout=120,
         no_check_hostname=False,
         dry_run=False,
         save_config=False,
    ):
    check_hostname = not no_check_hostname
    env = datapower.Environment(
        hostnames=appliances,
        credentials=credentials,
        timeout=timeout,
        check_hostname=check_hostname)
    allaterror = etree.fromstring('<LogEvents><Class class="LogLabel">all</Class><Priority>error</Priority></LogEvents>')
    for appliance in env.appliances:
        print(appliance.hostname)
        for domain in appliance.domains:
            changed = False
            print("\t{}".format(domain))
            config = appliance.get_config("LogTarget", "default-log", domain=domain, persisted=False)
            config = etree.fromstring(str(config))
            #config = config.xpath(r"/env:Envelope/env:Body/dp:response/dp:config/LogTarget", nsmap=nsmap)
            config = config.xpath(r'/*[local-name()="Envelope"]/*[local-name()="Body"]/*[local-name()="response"]/*[local-name()="config"]/*[local-name()="LogTarget"]')[0]
            if len(config.xpath('./LogEvents[not(./Class/text()="all") or not(./Priority/text()="error")]')):
                changed = True
                #pprint_xml(config)
                for nodeset in config.xpath(r'./*[local-name()="LogEvents"]'):
                    config.remove(nodeset)
                config.append(allaterror)
                #pprint_xml_str(etree.tostring(config))
                appliance.request.clear()
                request = appliance.request.request(domain=domain).set_config
                request.append(config)
                for nodeset in config.xpath(r'.//*'):
                    if "read-only" in nodeset.attrib:
                        nodeset.attrib.pop("read-only")
                #print(appliance.request)
                if not dry_run:
                    print(appliance.send_request(boolean=True))
                else:
                    pprint_xml(allaterror)
                print(" ")
            if save_config and not dry_run and changed:
                appliance.SaveConfig(domain=domain)

if __name__ == "__main__":
    interface = cli.Cli(main=main)
    try:
        interface.run()
    except SystemExit:
        pass
    except: 
        make_logger("error").exception("Sorry, an unhandled exception has occurred.")
        raise
