import re
import os
import sys
import csv
import urllib.request, urllib.error, urllib.parse
from glob import glob
from lxml import etree
from mast.cli import Cli
from collections import defaultdict
from mast.logging import make_logger
from mast.datapower import datapower
from mast.xor import xordecode
from xcfgdiff import main as xcfgdiff
from xsldiff import main as xsldiff
from compare_files import main as compare_files
from find_dynamically_referenced_objects import main as find_dynamically_referenced_objects

def get_obj_path(node):
    return '/{}/{}[@name="{}"]'.format(
        "/".join(
            anc.tag for anc in reversed(list(node.iterancestors()))
        ),
        node.tag,
        node.get("name")
    )

def get_cert_details(appliance, domain, cert_object):
    appliance.request.clear()
    req = appliance.request.request(domain=domain)
    req["do-view-certificate-details"]["certificate-object"](cert_object)
    return appliance.send_request()

XCFG_TEMPLATE = """<datapower-configuration version="3">
  <configuration>
  {}
  </configuration>
</datapower-configuration>"""

def main(
        credentials="",
        service_csv="",
        out_dir="",
        appliance_dir="",
        wrapcolumn=80,
        tabsize=4,
        no_only_differences=False,
        no_remove_namespaces=False,
        no_same_filenames=False,
    ):
    parser = etree.XMLParser(
        remove_blank_text=True,
        strip_cdata=False,
    )
    crypto_rows = [
        [
            "localfile",
            "class",
            "name",
            "password",
            "password alias",
            "filename",
            "subject",
            "issuer",
            "SANs",
            "not before",
            "not after",
        ]
    ]
    with open(service_csv, "rb") as fin:
        for row in csv.DictReader(fin):
            print(row)
            dp_out_dir = os.path.join(
                out_dir,
                row["zone"],
                row["environment"],
                row["hostname"],
                row["domain"],
            )
            if not os.path.exists(dp_out_dir):
                os.makedirs(dp_out_dir)
            appliance = datapower.DataPower(
                row["hostname"],
                credentials,
                check_hostname=False,
            )

            #############################################################
            # Get the domains config
            filename = os.path.join(
                dp_out_dir,
                "domain-config.xml"
            )
            config = appliance.get_config(domain=row["domain"])
            with open(filename, "wb") as fout:
                fout.write(str(config))

            #############################################################
            # Get the files from service directory
            command = " ".join([
                "mast",
                "contrib/fs-sync.py",
                "from_dp",
                "-a", appliance.hostname,
                "-c", credentials,
                "-n",
                "-l local:///{}".format(row["name"].split("_")[-1] if not appliance_dir else appliance_dir),
                "-o", os.path.join(dp_out_dir, "files"),
                "-d", row["domain"],
                "-r", "-i",
            ])
            os.system(command)

            #############################################################
            # Get the files from local:/
            command = " ".join([
                "mast",
                "contrib/fs-sync.py",
                "from_dp",
                "-a", appliance.hostname,
                "-c", credentials,
                "-n",
                "-l local:///",
                "-o", os.path.join(dp_out_dir, "files"),
                "-d", row["domain"],
                "-i",
            ])
            os.system(command)

            #############################################################
            # Export the service
            export = appliance.export(
                domain=row["domain"],
                obj=row["name"],
                object_class=row["type"],
                comment="{}-{}-{}-{}-{}-{}".format(
                    row["zone"],
                    row["environment"],
                    row["hostname"],
                    row["domain"],
                    row["type"],
                    row["name"],
                ),
                format="XML",
                persisted=False,
                all_files=False,
                referenced_files=False,
                referenced_objects=True,
            )
            out_filename = os.path.join(dp_out_dir, "{}.xcfg".format(row["name"]))
            with open(out_filename, "wb") as fout:
                fout.write(export)

            #############################################################
            # Get certificate details for all certificates
            print("\n*** Getting certificate details")
            tree = etree.parse(out_filename, parser)

            # crypto_details += "{}{}".format(out_filename, os.linesep)
            for cert_object in tree.xpath("//*[local-name() = 'CryptoCertificate' or local-name() = 'CryptoKey']"):
                _row = ['"{}"'.format(out_filename)]
                name = cert_object.get("name")
                _row.append('"{}"'.format(cert_object.tag))
                _row.append('"{}"'.format(name))

                # crypto_details += "{2}\t{0}: {1}{2}".format(cert_object.tag, name, os.linesep)

                password = cert_object.find("Password")
                password = "" if password is None else password.text
                _row.append('"{}"'.format(password))
                # crypto_details += "\t\tPASSWORD: {}{}".format(password, os.linesep)

                password_alias = cert_object.find("Alias")
                password_alias = "" if password_alias is None else password_alias.text
                _row.append('"{}"'.format(password_alias))
                # crypto_details += "\t\tPASSWORD_ALIAS: {}{}".format(password_alias, os.linesep)

                remotefile = cert_object.find("Filename")
                remotefile = "" if remotefile is None else remotefile.text
                _row.append('"{}"'.format(remotefile))
                # crypto_details += "\t\tFILENAME: {}{}".format(remotefile, os.linesep)

                if cert_object.tag == "CryptoCertificate":
                    try:
                        details = etree.fromstring(str(get_cert_details(appliance, row["domain"], cert_object.get("name"))))
                    except urllib.error.HTTPError:
                        print(("\tUnable to get details fpr {}".format(cert_object.get("name"))))
                        continue
                    subject = details.xpath(
                        "/*[local-name() = 'Envelope']"
                        "/*[local-name() = 'Body']"
                        "/*[local-name() = 'response']"
                        "/*[local-name() = 'view-certificate-details']"
                        "/CryptoCertificate"
                        "/CertificateDetails"
                        "/Subject"
                    )
                    subject = "" if not subject else subject[0].text
                    _row.append('"{}"'.format(subject))
                    # crypto_details += "\t\tSUBJECT: {}{}".format(subject, os.linesep)

                    issuer = details.xpath(
                        "/*[local-name() = 'Envelope']"
                        "/*[local-name() = 'Body']"
                        "/*[local-name() = 'response']"
                        "/*[local-name() = 'view-certificate-details']"
                        "/CryptoCertificate"
                        "/CertificateDetails"
                        "/Issuer"
                    )
                    issuer = "" if not issuer else issuer[0].text
                    _row.append('"{}"'.format(issuer))
                    # crypto_details += "\t\tISSUER: {}{}".format(issuer, os.linesep)

                    sans = details.xpath(
                        "/*[local-name() = 'Envelope']"
                        "/*[local-name() = 'Body']"
                        "/*[local-name() = 'response']"
                        "/*[local-name() = 'view-certificate-details']"
                        "/CryptoCertificate"
                        "/CertificateDetails"
                        "/Extensions"
                        "/Extension[@name='subjectAltName']"
                        "/item"
                    )
                    sans = [san.text for san in sans]
                    _row.append('"{}"'.format(" ".join(sans)))
                    # for san in sans:
                    #     crypto_details += "\t\tSAN: {}{}".format(san, os.linesep)

                    notbefore = details.xpath(
                        "/*[local-name() = 'Envelope']"
                        "/*[local-name() = 'Body']"
                        "/*[local-name() = 'response']"
                        "/*[local-name() = 'view-certificate-details']"
                        "/CryptoCertificate"
                        "/CertificateDetails"
                        "/NotBefore"
                    )
                    notbefore = "" if not notbefore else notbefore[0].text
                    _row.append('"{}"'.format(notbefore))
                    # crypto_details += "\t\tNOT BEFORE: {}{}".format(notbefore, os.linesep)

                    notafter = details.xpath(
                        "/*[local-name() = 'Envelope']"
                        "/*[local-name() = 'Body']"
                        "/*[local-name() = 'response']"
                        "/*[local-name() = 'view-certificate-details']"
                        "/CryptoCertificate"
                        "/CertificateDetails"
                        "/NotAfter"
                    )
                    notafter = "" if not notafter else notafter[0].text
                    _row.append('"{}"'.format(notafter))
                    # crypto_details += "\t\tNOT AFTER: {}{}".format(notafter, os.linesep)
                crypto_rows.append(_row)
        with open(os.path.join(out_dir, "crypto-details.csv"), "wb") as fp:
            for _row in crypto_rows:
                fp.write("{}{}".format(",".join(_row), os.linesep))


        with open(os.path.join(out_dir, "file-hashes.txt"), "wb") as fp:
            sys.stdout = fp
            #############################################################
            # Diff xcfg files
            print(("{}*** Comparing Configuration".format(os.linesep)))
            diff_dir = os.path.join(out_dir, "diffs", "xcfg")
            if not os.path.exists(diff_dir):
                os.makedirs(diff_dir)
            xcfgdiff(
                xcfg_globs=[
                    os.path.join(out_dir, "*", "*", "*", "*", "*.xcfg")
                ],
                out_dir=diff_dir,
                wrapcolumn=wrapcolumn,
                tabsize=tabsize,
                no_only_differences=no_only_differences,
                no_remove_namespaces=no_remove_namespaces,
            )

            #############################################################
            # Diff xsl files
            print(("{}*** Comparing Stylesheets".format(os.linesep)))
            diff_dir = os.path.join(out_dir, "diffs", "xsl")
            if not os.path.exists(diff_dir):
                os.makedirs(diff_dir)
            xsldiff(
                xsl_globs=[
                    os.path.join(out_dir, "*", "*", "*", "*", "files", "*", "local", "*", "*.xsl*")
                ],
                out_dir=diff_dir,
                wrapcolumn=wrapcolumn,
                tabsize=tabsize,
                no_only_differences=no_only_differences,
                no_same_filenames=no_same_filenames,
            )
            print(("{}*** Second Comparing Stylesheets".format(os.linesep)))
            diff_dir = os.path.join(out_dir, "diffs", "xsl")
            if not os.path.exists(diff_dir):
                os.makedirs(diff_dir)
            xsldiff(
                xsl_globs=[
                    os.path.join(out_dir, "*", "*", "*", "*", "files", "*", "local", "*.xsl*")
                ],
                out_dir=diff_dir,
                wrapcolumn=wrapcolumn,
                tabsize=tabsize,
                no_only_differences=no_only_differences,
                no_same_filenames=no_same_filenames,
            )

            #############################################################
            # Diff xml files
            print("\n*** Comparing XML documents")
            diff_dir = os.path.join(out_dir, "diffs", "xml")
            if not os.path.exists(diff_dir):
                os.makedirs(diff_dir)
            compare_files(
                pattern=os.path.join(out_dir, "*", "*", "*", "*", "files", "*", "local", "*", "*.xml"),
                out_dir=diff_dir,
                wrapcolumn=wrapcolumn,
                tabsize=tabsize,
            )
            print("\n*** Comparing XML documents")
            diff_dir = os.path.join(out_dir, "diffs", "xml")
            if not os.path.exists(diff_dir):
                os.makedirs(diff_dir)
            compare_files(
                pattern=os.path.join(out_dir, "*", "*", "*", "*", "files", "*", "local", "*.xml"),
                out_dir=diff_dir,
                wrapcolumn=wrapcolumn,
                tabsize=tabsize,
            )
            sys.stdout = sys.__stdout__

        #############################################################
        # Find all Load Balancer Groups
        print("\n*** Finding all Load Balancer Groups")
        lbg_out_file = os.path.join(out_dir, "LBGs.csv")
        pattern = os.path.join(out_dir, "*", "*", "*", "*", "*.xcfg")
        rows = []
        rows.append("localfile, LBG{}".format(os.linesep))
        for filename in glob(pattern):
            lbg_dir = os.path.join(
                os.path.dirname(filename),
                "LBG",
            )
            if not os.path.exists(lbg_dir):
                os.makedirs(lbg_dir)
            print(("{}:".format(filename)))
            tree = etree.parse(filename, parser)
            for node in tree.xpath("//LoadBalancerGroup"):
                name = node.get("name")
                print(("\t{}".format(name)))
                rows.append("{},{}{}".format(filename, name, os.linesep))
                _filename = os.path.join(
                    lbg_dir,
                    "{}.xcfg".format(name),
                )
                with open(_filename, "wb") as fp:
                    fp.write(
                        XCFG_TEMPLATE.format(
                            etree.tostring(node, pretty_print=True)
                        )
                    )
        with open(lbg_out_file, "wb") as fp:
            for row in rows:
                fp.write("{}".format(row))

        #############################################################
        # Find unreferenced files
        print("\n*** Looking for dynamically referenced objects")
        find_dynamically_referenced_objects(
            config_globs=[
                os.path.join(out_dir, "*", "*", "*", "*", "*.xml"),
            ],
            out_file=os.path.join(out_dir, "dynamically_referenced_objects.txt"),
        )

        #############################################################
        # Find cert:/// file references
        cert_matches = defaultdict(list)

        for dirname in glob(os.path.join(out_dir, "*", "*", "*", "*")):
            for root, dirs, filenames in os.walk(dirname):
                for filename in [os.path.join(root, f) for f in filenames]:
                    with open(filename, "r") as fp:
                        for line in fp:
                            if "cert:///" in line:
                                for match in re.findall('.*?(cert:///.*?)[<"]', line):
                                    cert_matches[match].append(filename)
        cert_file = os.path.join(out_dir, "referenced_cert_files.txt")
        with open(cert_file, "wb") as fp:
            for cert, filenames in list(cert_matches.items()):
                fp.write("{}{}".format(cert, os.linesep))
                for filename in filenames:
                    fp.write("\t{}{}".format(filename, os.linesep))

if __name__ == "__main__":
    cli = Cli(main=main)
    try:
        cli.run()
    except SystemExit:
        pass
    except:
        make_logger("error").exception("Sorry, an unhandled exception occurred.")
        raise
