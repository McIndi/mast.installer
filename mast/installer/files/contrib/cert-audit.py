import OpenSSL
import openpyxl
import mast.cli as cli
from time import sleep
from mast.logging import make_logger
import xml.etree.cElementTree as etree
import mast.datapower.datapower as datapower
from dateutil import parser, tz, relativedelta
from datetime import datetime
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
         out_file="tmp/cert-audit.xlsx",
         delay=0.5,
         date_time_format="%A, %B %d, %Y, %X",
         localtime=False):

    check_hostname = not no_check_hostname
    env = datapower.Environment(
        appliances,
        credentials,
        timeout,
        check_hostname=check_hostname)

    wb = openpyxl.Workbook()
    ws = wb.get_active_sheet()
    header_row = [
        "appliance",
        "domain",
        "certificate-object",
        "filename",
        "subject",
        "not_before",
        "not_after",
        "issuer",
        "is-expired",
        "time-since-expiration",
        "time-until-expiration"]
    ws.append(header_row)

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

            # Filter out disabled objects because the results won't change,
            # but we will perform less network traffic
            certs = filter(
                lambda x: x.find("mAdminState").text == "enabled",
                certs)

            for cert in certs:
                logger.info("Exporting cert {}".format(cert))
                filename = cert.find("Filename").text
                name = cert.get("name")
                _filename = name
                print "\t\t", name
                row = [appliance.hostname, domain, name, filename]

                appliance.CryptoExport(
                    domain=domain,
                    ObjectType="cert",
                    ObjectName=name,
                    OutputFilename=_filename)
                logger.info("Finished exporting cert {}".format(cert))
                try:
                    logger.info(
                        "Retrieving file {}".format(
                            "temporary:///{}".format(_filename)))
                    cert = appliance.getfile(
                        domain,
                        "temporary:///{}".format(_filename))
                    logger.info(
                        "Finished retrieving file {}".format(
                            "temporary:///{}".format(_filename)))
                    logger.info(
                        "Attempting to delete file {}".format(
                            "temporary:///{}".format(_filename)))
                    appliance.DeleteFile(
                        domain=domain,
                        File="temporary:///{}".format(_filename))
                    logger.info(
                        "Finished deleting file {}".format(
                            "temporary:///{}".format(_filename)))
                except UnboundLocalError:
                    # This most likely means the file did not exist for
                    # some reason (skip)
                    continue
                except:
                    logger.exception("An unhandled exception has occurred")
                    print appliance.history
                    print "SKIPPING CERT"
                    continue
                cert = etree.fromstring(cert)
                _contents = insert_newlines(cert.find("certificate").text)
                certificate = \
                    "-----BEGIN CERTIFICATE-----\n" +\
                    _contents +\
                    "\n-----END CERTIFICATE-----\n"
                _cert = OpenSSL.crypto.load_certificate(
                    OpenSSL.crypto.FILETYPE_PEM,
                    certificate)
                subject = "'{}'".format(
                    ";".join(
                        ["=".join(x)
                         for x in _cert.get_subject().get_components()]))
                issuer = "'{}'".format(
                    ";".join(
                        ["=".join(x)
                         for x in _cert.get_issuer().get_components()]))
                local_tz = tz.tzlocal()
                utc_tz = tz.tzutc()
                notBefore_utc = parser.parse(_cert.get_notBefore())
                notBefore_local = notBefore_utc.astimezone(local_tz)

                notAfter_utc = parser.parse(_cert.get_notAfter())
                notAfter_local = notAfter_utc.astimezone(local_tz)
                if localtime:
                    notAfter = notAfter_local.strftime(date_time_format)
                    notBefore = notBefore_local.strftime(date_time_format)
                else:
                    notAfter = notAfter_utc.strftime(date_time_format)
                    notBefore = notBefore_utc.strftime(date_time_format)

                if _cert.has_expired():
                    time_since_expiration = datetime.utcnow().replace(tzinfo=utc_tz) - notAfter_utc
                    time_until_expiration = 0
                else:
                    time_until_expiration = notAfter_utc - datetime.utcnow().replace(tzinfo=utc_tz)
                    time_since_expiration = 0
                row.extend(
                    [subject,
                     notBefore,
                     notAfter,
                     issuer,
                     str(_cert.has_expired()),
                     str(time_since_expiration),
                     str(time_until_expiration)])
                ws.append(row)
                sleep(delay)
    wb.save(out_file)


if __name__ == "__main__":
    _cli = cli.Cli(main=main)
    _cli.run()
