#", "-*-", "coding:", "utf-8", "-*-
"""
"""
import re
import os
import OpenSSL
import openpyxl
import pandas as pd
from time import sleep
from mast.cli import Cli
from mast.logging import make_logger
import xml.etree.cElementTree as etree
import mast.datapower.datapower as datapower
from getconfig import main as getconfig


logger = make_logger("mast.crypto-audit")

def cert_file_audit(appliances=[],
                    credentials=[],
                    timeout=120,
                    no_check_hostname=False,
                    out_file=os.path.join("tmp", "cert-file-audit.xlsx")):
    locations = ["cert:", "pubcert:", "sharedcert:"]
    check_hostname = not no_check_hostname
    env = datapower.Environment(appliances,
                                credentials,
                                timeout,
                                check_hostname=check_hostname)

    header_row = ["appliance",
                  "domain",
                  "filename",
                  "base-filename",
                  "size",
                  "modified"]
    rows = []

    for appliance in env.appliances:
        print((appliance.hostname))
        domain = "default"

        for location in locations:
            print(("\t{}".format(location)))
            filestore = appliance.get_filestore(domain=domain,
                                                location=location)
            _location = filestore.xml.find(datapower.FILESTORE_XPATH)
            if _location is None:
                continue
            if _location.findall("./file") is not None:
                for _file in _location.findall("./file"):
                    dir_name = _location.get("name")
                    filename = _file.get("name")
                    filename = "/".join((dir_name, filename))
                    filename = re.sub(r":[/]*", ":///", filename)
                    base_filename = filename.split("/")[-1]
                    print(("\t\t{}".format(filename)))
                    size = _file.find("size").text
                    modified = _file.find("modified").text
                    rows.append([appliance.hostname,
                                 domain,
                                 filename,
                                 base_filename,
                                 size,
                                 modified])
            for directory in _location.findall(".//directory"):
                dir_name = directory.get("name")
                print(("\t\t{}".format(dir_name)))
                for _file in directory.findall(".//file"):
                    filename = _file.get("name")
                    filename = "/".join((dir_name, filename))
                    filename = re.sub(r":[/]*", ":///", filename)
                    base_filename = filename.split("/")[-1]
                    # Infer domain from second segment of path if in cert:
                    _domain = domain
                    if location == "cert:":
                        _domain = filename.replace("///", "/").split("/")[1]
                        filename = filename.replace(_domain+"/", "")
                    print(("\t\t\t{}".format(filename)))
                    size = _file.find("size").text
                    modified = _file.find("modified").text

                    rows.append([appliance.hostname,
                                 _domain,
                                 filename,
                                 base_filename,
                                 size,
                                 modified])
    wb = openpyxl.Workbook()
    ws = wb.get_active_sheet()
    ws.title = "CertFileAudit"
    ws.append(header_row)
    for row in rows:
        ws.append(row)
    wb.save(out_file)

def insert_newlines(string, every=64):
    return '\n'.join(string[i:i+every] for i in range(0, len(string), every))


def cert_audit(appliances=[],
               credentials=[],
               timeout=120,
               no_check_hostname=False,
               domains=[],
               out_file="tmp/cert-audit.xlsx",
               delay=0.5):

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
        "SANs",
        "not-before",
        "not-after",
        "issuer"]
    ws.append(header_row)

    for appliance in env.appliances:
        logger.info("Checking appliance {}".format(appliance.hostname))
        print((appliance.hostname))
        _domains = domains
        if "all-domains" in domains:
            _domains = appliance.domains
        for domain in _domains:
            logger.info("In domain {}".format(domain))
            print(("\t", domain))
            config = appliance.get_config("CryptoCertificate", domain=domain)
            certs = [x for x in config.xml.findall(datapower.CONFIG_XPATH)]

            # Filter out disabled objects because the results won't change,
            # but we will perform less network traffic
            certs = [x for x in certs if x.find("mAdminState").text == "enabled"]

            for cert in certs:
                logger.info("Exporting cert {}".format(cert))
                filename = cert.find("Filename").text
                filename = re.sub(r":[/]*", ":///", filename)
                name = cert.get("name")
                _filename = name
                print(("\t\t", name))
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
                    print((appliance.history))
                    print("SKIPPING CERT")
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
                sans = []
                ext_count = _cert.get_extension_count()
                for i in range(0, ext_count):
                    ext = _cert.get_extension(i)
                    if 'subjectAltName' in str(ext.get_short_name()):
                        sans.append(ext.__str__())
                sans = "\n".join(sans)
                issuer = "'{}'".format(
                    ";".join(
                        ["=".join(x)
                         for x in _cert.get_issuer().get_components()]))
                row.extend(
                    [subject,
                    sans,
                     _cert.get_notBefore(),
                     _cert.get_notAfter(),
                     issuer])
                ws.append(row)
                sleep(delay)
    wb.save(out_file)


default_out_file = os.path.join("tmp", "thourough-cert-audit.xlsx")
def main(appliances=[],
         credentials=[],
         timeout=120,
         no_check_hostname=False,
         obfuscate_passwords=False,
         out_file=default_out_file,
         clean_artifacts=False):
    # 1. perform the cert-file-audit
    print("EXAMINING FILESYSTEMS")
    cert_file_audit_file = os.path.join("tmp", "base-cert-file-audit.xlsx")
    cert_file_audit(appliances=appliances,
                    credentials=credentials,
                    timeout=timeout,
                    no_check_hostname=no_check_hostname,
                    out_file=cert_file_audit_file)
    # 2. Perform the cert-audit
    #      * Left-join results to cert-file-audit
    print("EXAMINING CERTIFICATES")

    cert_audit_file = os.path.join("tmp", "cert-audit.xlsx")
    cert_audit(appliances=appliances,
               credentials=credentials,
               timeout=timeout,
               no_check_hostname=no_check_hostname,
               domains=["all-domains"],
               out_file=cert_audit_file)
    df_1 = pd.read_excel(cert_file_audit_file)
    df_2 = pd.read_excel(cert_audit_file)
    df_2.rename(columns={"certificate-object": "Certificate"}, inplace=True)
    keys = list(df_2.keys())
    if "filename" in keys:
        keys.remove("appliance")
        keys.remove("domain")
        keys.remove("filename")
        keys.remove("Certificate")
        df_2.rename(columns={key:"CryptoCertificate-{}".format(key) for key in keys}, inplace=True)
        final_df = pd.merge(df_1,
                            df_2,
                            on=["appliance", "domain", "filename"],
                            how="left")

    # rename certificate-object to Certificate

    # 3. loop through object_classes
    #      * getconfig object class
    #      * left-join to cert-file-audit
    print("EXAMINING KEYS")
    object_class_xlsx = os.path.join("tmp",
                                     "CryptoKey-config.xlsx")
    getconfig(appliances=appliances,
              credentials=credentials,
              object_classes=["CryptoKey"],
              domains=["all-domains"],
              timeout=timeout,
              no_check_hostname=no_check_hostname,
              out_file=object_class_xlsx,
              no_prepend_timestamp=True,
              obfuscate_password=obfuscate_passwords)
    df = pd.read_excel(object_class_xlsx)
    df.rename(columns={"Filename": "filename", "Object Name": "Key"}, inplace=True)
    df.drop('Object Class', axis=1, inplace=True)
    keys = list(df.keys())
    if "filename" in keys:
        keys.remove("filename")
        keys.remove("Key")
        keys.remove("appliance")
        keys.remove("domain")
        df.rename(columns={key:"CryptoKey-{}".format(key) for key in keys}, inplace=True)
        final_df = pd.merge(final_df,
                            df,
                            on=["appliance", "domain", "filename"],
                            how="left")
    if clean_artifacts:
        os.remove(object_class_xlsx )

    print("EXAMINING CryptoSSKeys")
    object_class_xlsx = os.path.join("tmp",
                                     "CryptoSSKey-config.xlsx")
    getconfig(appliances=appliances,
              credentials=credentials,
              object_classes=["CryptoSSKey"],
              domains=["all-domains"],
              timeout=timeout,
              no_check_hostname=no_check_hostname,
              out_file=object_class_xlsx,
              no_prepend_timestamp=True,
              obfuscate_password=obfuscate_passwords)
    df = pd.read_excel(object_class_xlsx)
    print(df)
    df.rename(columns={"Object Name": "CryptoSSKey", "Filename": "filename"}, inplace=True)
    df.drop('Object Class', axis=1, inplace=True)
    keys = list(df.keys())
    if "filename" in keys:
        keys.remove("filename")
        keys.remove("CryptoSSKey")
        keys.remove("appliance")
        keys.remove("domain")
        df.rename(columns={key:"CryptoSSKey-{}".format(key) for key in keys}, inplace=True)
        final_df = pd.merge(final_df,
                            df,
                            on=["appliance", "domain", "filename"],
                            how="left")
    if clean_artifacts:
        os.remove(object_class_xlsx )

    print("EXAMINING CryptoValCreds")
    object_class_xlsx = os.path.join("tmp",
                                     "CryptoValCred-config.xlsx")
    getconfig(appliances=appliances,
              credentials=credentials,
              object_classes=["CryptoValCred"],
              domains=["all-domains"],
              timeout=timeout,
              no_check_hostname=no_check_hostname,
              out_file=object_class_xlsx,
              no_prepend_timestamp=True,
              obfuscate_password=obfuscate_passwords)
    df = pd.read_excel(object_class_xlsx)
    df.rename(columns={"Object Name": "ValCredential"}, inplace=True)
    df.drop('Object Class', axis=1, inplace=True)
    df.drop('Certificate[@class]', axis=1, inplace=True)
    keys = list(df.keys())
    if "Certificate" in keys:
        keys.remove("ValCredential")
        keys.remove("Certificate")
        keys.remove("appliance")
        keys.remove("domain")
        df.rename(columns={key:"CryptoValCred-{}".format(key) for key in keys}, inplace=True)
        final_df = pd.merge(final_df,
                            df,
                            on=["appliance", "domain", "Certificate"],
                            how="left")
    if clean_artifacts:
        os.remove(object_class_xlsx )

    print("EXAMINING CryptoIdCreds")
    object_class_xlsx = os.path.join("tmp",
                                     "CryptoIdentCred-config.xlsx")
    getconfig(appliances=appliances,
              credentials=credentials,
              object_classes=["CryptoIdentCred"],
              domains=["all-domains"],
              timeout=timeout,
              no_check_hostname=no_check_hostname,
              out_file=object_class_xlsx,
              no_prepend_timestamp=True,
              obfuscate_password=obfuscate_passwords)
    df = pd.read_excel(object_class_xlsx)
    df.rename(columns={"Object Name": "IdentCredential"}, inplace=True)
    df.drop('Key[@class]', axis=1, inplace=True)
    df.drop('Object Class', axis=1, inplace=True)
    df.drop('Certificate[@class]', axis=1, inplace=True)
    keys = list(df.keys())
    if "Key" in keys:
        keys.remove("IdentCredential")
        keys.remove("Certificate")
        keys.remove("appliance")
        keys.remove("domain")
        keys.remove("Key")
        df.rename(columns={key:"CryptoIdCred-{}".format(key) for key in keys}, inplace=True)
        final_df = pd.merge(final_df,
                            df,
                            on=["appliance", "domain", "Key", "Certificate"],
                            how="left")
    if clean_artifacts:
        os.remove(object_class_xlsx )

    print("EXAMINING CryptoProfiles")
    object_class_xlsx = os.path.join("tmp",
                                     "CryptoProfile-config.xlsx")
    getconfig(appliances=appliances,
              credentials=credentials,
              object_classes=["CryptoProfile"],
              domains=["all-domains"],
              timeout=timeout,
              no_check_hostname=no_check_hostname,
              out_file=object_class_xlsx,
              no_prepend_timestamp=True,
              obfuscate_password=obfuscate_passwords)
    df = pd.read_excel(object_class_xlsx)
    df.rename(columns={"Object Name": "CryptoProfile"}, inplace=True)
    if "ValCredential" in list(df.keys()):
        df.drop('Object Class', axis=1, inplace=True)
        df.drop('IdentCredential[@class]', axis=1, inplace=True)
        df.drop('ValCredential[@class]', axis=1, inplace=True)
        keys = list(df.keys())
        keys.remove("CryptoProfile")
        keys.remove("IdentCredential")
        keys.remove("appliance")
        keys.remove("domain")
        keys.remove("ValCredential")
        df.rename(columns={key:"CryptoProfile-{}".format(key) for key in keys}, inplace=True)
        final_df = pd.merge(final_df,
                            df,
                            on=["appliance", "domain", "IdentCredential", "ValCredential"],
                            how="left")
    if clean_artifacts:
        os.remove(object_class_xlsx )

    # 4. output excel file
    print(("WRITING {}".format(os.path.abspath(out_file))))
    final_df.to_excel(out_file, index=False)

    if clean_artifacts:
        os.remove(cert_file_audit_file)
        os.remove(cert_audit_file)

if __name__ == "__main__":
    cli = Cli(main=main)
    try:
        cli.run()
    except SystemExit:
        pass
    except:
        make_logger("error").exception("An unhandled exception occurred!")
        raise
