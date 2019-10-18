import os
import json
import OpenSSL
from lxml import etree
from mast.cli import Cli
from mast.util import _s, _b
from datetime import datetime
from dateutil import parser, tz
from collections import defaultdict
from mast.logging import make_logger
import mast.datapower.datapower as datapower

def insert_newlines(string, every=64):
    return '\n'.join(string[i:i+every] for i in range(0, len(string), every))

def tree():
    return defaultdict(tree)

def main(appliances=[],
         credentials=[],
         timeout=120,
         no_check_hostname=False,
         domains=[],
         out_file="tmp/cert-audit.json",
         delay=0.5,
         date_time_format="%A, %B %d, %Y, %X",
         localtime=False,
         limit=30,
     ):
    logger = make_logger("cert-recurse")
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
            certs = [x for x in config.xpath(".//CryptoCertificate")]

            # Filter out disabled objects because the results won't change,
            # but we will perform less network traffic
            certs = [x for x in certs if x.find("mAdminState").text == "enabled"]

            for cert in certs:
                logger.info("Exporting cert {}".format(cert))
                filename = cert.find("Filename").text
                name = cert.get("name")
                print(("\t\tCryptoCertificate: {}".format(name)))
                _filename = name

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
                    cert_file = appliance.getfile(
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
                except:
                    logger.exception("An unhandled exception has occurred")
                    cert_node = out[hostname][domain]["CryptoCertificate"] = {
                        "name": cert.get("name"),
                        "error": "COULD NOT EXPORT"
                    }
                    continue
                cert_export = etree.fromstring(_b(cert_file))
                _contents = insert_newlines(cert_export.find("certificate").text)
                certificate = \
                    "-----BEGIN CERTIFICATE-----\n" +\
                    _contents +\
                    "\n-----END CERTIFICATE-----\n"
                _cert = OpenSSL.crypto.load_certificate(
                    OpenSSL.crypto.FILETYPE_PEM,
                    certificate)
                subject = "'{}'".format(
                    ";".join(
                        ["=".join((_s(x), _s(y)))
                         for x, y in _cert.get_subject().get_components()]))
                issuer = "'{}'".format(
                    ";".join(
                        ["=".join((_s(x), _s(y)))
                         for x, y in _cert.get_issuer().get_components()]))
                serial_number = _cert.get_serial_number()
                sans = []
                ext_count = _cert.get_extension_count()
                for i in range(0, ext_count):
                    ext = _cert.get_extension(i)
                    if 'subjectAltName' in str(ext.get_short_name()):
                        sans.append(ext.__str__())
                sans = "\n".join(sans)
                try:
                    signature_algorithm = _cert.get_signature_algorithm()
                except AttributeError:
                    signature_algorithm = ""
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
                    time_since_expiration = time_since_expiration.days
                    time_until_expiration = 0
                else:
                    time_until_expiration = notAfter_utc - datetime.utcnow().replace(tzinfo=utc_tz)
                    time_until_expiration = time_until_expiration.days
                    time_since_expiration = 0

                if time_until_expiration <= limit:
                    cert_node = out[hostname][domain]["CryptoCertificate: {}".format(name)]
                    cert_node["serial_number"] = str(serial_number)
                    cert_node["subject"] = subject
                    cert_node["sans"] = sans
                    cert_node["signature_algorithm"] = _s(signature_algorithm)
                    cert_node["notBefore"] = notBefore
                    cert_node["notAfter"] = notAfter
                    cert_node["issuer"] = issuer
                    cert_node["has_expired"] = _cert.has_expired()
                    cert_node["time_since_expiration"] = time_since_expiration
                    cert_node["time_until_expiration"] = time_until_expiration
                    recurse_config(config, cert, cert_node)
    with open(out_file, "w") as fp:
        json.dump(out, fp, indent=4)

def recurse_tree(tree):
    ret = {}
    for k, v in tree.items():
        if isinstance(v, defaultdict):
            ret.update(dict(v))
            recurse_tree(v)
        else:
            print(v)
    return ret

def recurse_config(config, cert, cert_node, level=1):
    klass = cert.tag
    name = cert.get("name")
    for match in config.xpath(".//*[local-name()='config']/*[.//*/@class='{}' and .//*/text()='{}']".format(klass, name)):
        print(("{}{}: {}".format("\t"*(2+level), match.tag, match.get("name"))))
        _node = cert_node["{}: {}".format(match.tag, match.get("name"))]
        recurse_config(config, match, _node, level=level+1)

if __name__ == "__main__":
    cli = Cli(main=main)
    try:
        cli.run()
    except SystemExit:
        pass
    except:
        make_logger("error").exception("An unhandled exception has occurred")
        raise
