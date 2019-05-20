import re
import os
import csv
from glob import glob
from mast.cli import Cli
from mast.logging import make_logger
from mast.datapower import datapower
from mast.xor import xordecode
from xcfgdiff import main as xcfgdiff
from xsldiff import main as xsldiff
from compare_files import main as compare_files
from find_dynamically_referenced_objects import main as find_dynamically_referenced_objects

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
    with open(service_csv, "rb") as fin:
        for row in csv.DictReader(fin):
            print row
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
            # Get the domains config
            filename = os.path.join(
                dp_out_dir,
                "domain-config.xml"
            )
            config = appliance.get_config(domain=row["domain"])
            with open(filename, "wb") as fout:
                fout.write(str(config))

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
            with open(os.path.join(dp_out_dir, "{}.xcfg".format(row["name"])), "wb") as fout:
                fout.write(export)
        # Diff xcfg files
        print("*** Comparing Configuration")
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
        # Diff xsl files
        print("*** Comparing Stylesheets")
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
        print("*** Second Comparing Stylesheets")
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
        # Diff xml files
        print("*** Comparing XML documents")
        diff_dir = os.path.join(out_dir, "diffs", "xml")
        if not os.path.exists(diff_dir):
            os.makedirs(diff_dir)
        compare_files(
            pattern=os.path.join(out_dir, "*", "*", "*", "*", "files", "*", "local", "*", "*.xml"),
            out_dir=diff_dir,
            wrapcolumn=wrapcolumn,
            tabsize=tabsize,
        )
        print("*** Comparing XML documents")
        diff_dir = os.path.join(out_dir, "diffs", "xml")
        if not os.path.exists(diff_dir):
            os.makedirs(diff_dir)
        compare_files(
            pattern=os.path.join(out_dir, "*", "*", "*", "*", "files", "*", "local", "*.xml"),
            out_dir=diff_dir,
            wrapcolumn=wrapcolumn,
            tabsize=tabsize,
        )
        # Find unreferenced files
        print("*** Looking for dynamically referenced objects")
        find_dynamically_referenced_objects(
            config_globs=[
                os.path.join(out_dir, "*", "*", "*", "*", "*.xml"),
            ],
            out_file=os.path.join(out_dir, "diffs", "dynamically_referenced_objects.txt"),
        )
        # Find cert:/// files
        cert_matches = set()
        local_matches = set()

        for dirname in glob(os.path.join(out_dir, "*", "*", "*", "*")):
            for root, dirs, filenames in os.walk(dirname):
                for filename in [os.path.join(root, f) for f in filenames]:
                    with open(filename, "r") as fp:
                        for line in fp:
                            if "cert:///" in line:
                                for match in re.findall('.*?(cert:///.*?)[<"]', line):
                                    cert_matches.add(line)
                            if "local:///" in line:
                                for match in re.findall('.*?(local:///.*?)[<"]', line):
                                    local_matches.add(line)
        cert_file = os.path.join(out_dir, "diffs", "referenced_certs.txt")
        local_file = os.path.join(out_dir, "diffs", "referenced_local_files.txt")
        with open(cert_file, "wb") as fp:
            for match in cert_matches:
                fp.write("{}{}".format(match, os.linesep))
        with open(local_file, "wb") as fp:
            for match in local_matches:
                fp.write("{}{}".format(match, os.linesep))

if __name__ == "__main__":
    cli = Cli(main=main)
    try:
        cli.run()
    except SystemExit:
        pass
    except:
        make_logger("error").exception("Sorry, an unhandled exception occurred.")
        raise
