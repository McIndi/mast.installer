import os
import re
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


def main(appliances=[],
         credentials=[],
         timeout=120,
         no_check_hostname=False,
         domains=[],
         out_dir=".",
         delay=0.5):
    check_hostname = not no_check_hostname
    env = datapower.Environment(appliances,
                                credentials,
                                timeout,
                                check_hostname=check_hostname)

    for appliance in env.appliances:
        logger.info("Checking appliance {}".format(appliance.hostname))
        print appliance.hostname

        _domains = domains
        if "all-domains" in domains:
            _domains = appliance.domains

        for domain in _domains:
            logger.info("In domain {}".format(domain))
            print "\t", domain

            # Get a list of all certificates in this domain
            config = appliance.get_config("CryptoCertificate", domain=domain)
            certs = [x for x in config.xml.findall(datapower.CONFIG_XPATH)]
            if not certs:
                continue

            # Create a directory structure $out_dir/hostname/domain
            dir_name = os.path.join(out_dir, appliance.hostname, domain)
            if not os.path.exists(dir_name):
                os.makedirs(dir_name)

            for cert in certs:
                logger.info("Exporting cert {}".format(cert))

                # Get filename as it will appear locally
                filename = cert.find("Filename").text
                out_file = re.sub(r":[/]*", "/", filename)
                out_file = out_file.split("/")
                out_file = os.path.join(dir_name, *out_file)

                # extract directory name as it will appear locally
                _out_dir = out_file.split(os.path.sep)[:-1]
                _out_dir = os.path.join(*_out_dir)
                # Create the directory if it doesn't exist
                if not os.path.exists(_out_dir):
                    os.makedirs(_out_dir)

                name = cert.get("name")
                print "\t\t", name
                export = appliance.CryptoExport(domain=domain,
                                                ObjectType="cert",
                                                ObjectName=name,
                                                OutputFilename=name)
                # TODO: Test export and handle failure
                logger.info("Finished exporting cert {}".format(cert))
                try:
                    logger.info(
                        "Retrieving file temporary:///{}".format(name))
                    cert = appliance.getfile(domain,
                                             "temporary:///{}".format(name))
                    logger.info(
                        "Finished retrieving file temporary:///{}".format(
                            name))
                    logger.info(
                        "Attempting to delete file temporary:///{}".format(
                            name))
                    appliance.DeleteFile(domain=domain,
                                         File="temporary:///{}".format(name))
                    logger.info(
                        "Finished deleting file temporary:///{}".format(name))
                except UnboundLocalError:
                    # This most likely means the file did not exist
                    # for some reason (skip)
                    continue
                except:
                    logger.exception("An unhandled exception has occurred")
                    print appliance.history
                    print "SKIPPING CERT"
                    continue
                cert = etree.fromstring(cert)
                with open(out_file, "w") as fout:
                    _contents = insert_newlines(cert.find("certificate").text)
                    contents = "{}\n{}\n{}\n".format(
                        "-----BEGIN CERTIFICATE-----",
                        _contents,
                        "-----END CERTIFICATE-----")
                    fout.write(contents)

if __name__ == "__main__":
    _cli = cli.Cli(main=main)
    _cli.run()
