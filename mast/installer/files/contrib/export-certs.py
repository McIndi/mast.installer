import os
import mast.cli as cli
from mast.logging import make_logger
import mast.datapower.datapower as datapower
from time import sleep
import xml.etree.cElementTree as etree

from mast.timestamp import Timestamp

t = Timestamp()
logger = make_logger("mast.export-certs")

def insert_newlines(string, every=64):
    return '\n'.join(string[i:i+every] for i in xrange(0, len(string), every))

def main(appliances=[], credentials=[], timeout=120,
    no_check_hostname=False, domains=[], out_dir=".", delay=0.5):
    check_hostname = not no_check_hostname
    env = datapower.Environment(appliances, credentials, timeout, check_hostname=check_hostname)

    for appliance in env.appliances:
        logger.info("Checking appliance {}".format(appliance.hostname))
        print appliance.hostname
        _domains = domains
        if "all-domains" in domains:
            _domains = appliance.domains
        for domain in _domains:
            logger.info("In domain {}".format(domain))
            print "\t", domain
            config = appliance.get_config("CryptoCertificate", domain=domain)
            certs = [x for x in config.xml.findall(datapower.CONFIG_XPATH)]
            dir_name = os.path.join(out_dir, appliance.hostname, domain)
            if not os.path.exists(dir_name):
                os.makedirs(dir_name)
            for cert in certs:
                logger.info("Exporting cert {}".format(cert))
                filename = cert.find("Filename").text
                name = cert.get("name")
                _filename = name
                print "\t\t", name
                out_file = os.path.join(dir_name, "{}_-_{}".format(_filename, filename.split("/")[-1]))
                export = appliance.CryptoExport(domain=domain, ObjectType="cert", ObjectName=name, OutputFilename=_filename)
                logger.info("Finished exporting cert {}".format(cert))
                try:
                    logger.info("Retrieving file {}".format("temporary:///{}".format(_filename)))
                    cert = appliance.getfile(domain, "temporary:///{}".format(_filename))
                    logger.info("Finished retrieving file {}".format("temporary:///{}".format(_filename)))
                    logger.info("Attempting to delete file {}".format("temporary:///{}".format(_filename)))
                    appliance.DeleteFile(domain=domain, File="temporary:///{}".format(_filename))
                    logger.info("Finished deleting file {}".format("temporary:///{}".format(_filename)))
                except UnboundLocalError:
                    # This most likely means the file did not exist for some reason (skip)
                    continue
                except:
                    logger.exception("An unhandled exception has occurred")
                    print appliance.history
                    print "SKIPPING CERT"
                    continue
                cert = etree.fromstring(cert)
                with open(out_file, "w") as fout:
                    _contents = insert_newlines(cert.find("certificate").text)
                    contents = "-----BEGIN CERTIFICATE-----\n" + _contents + "\n-----END CERTIFICATE-----\n"
                    fout.write(contents)

if __name__ == "__main__":
    _cli = cli.Cli(main=main)
    _cli.run()
