import os
from glob import glob
from lxml import etree
from mast.cli import Cli
from mast.logging import make_logger
from mast.datapower.datapower import Environment

def get_obj_path(node):
    return '/{}/{}[@name="{}"]'.format(
        "/".join(
            anc.tag for anc in reversed(list(node.iterancestors()))
        ),
        node.tag,
        node.get("name")
    )

def main(
        config_globs=[],
        out_file=os.path.join("tmp", "found_passwords.csv")
    ):
    parser = etree.XMLParser(
        remove_blank_text=True,
        strip_cdata=False,
    )

    rows = []
    rows.append("localfile, xpath, remotefile, password")
    for pattern in config_globs:
        for localfile in glob(pattern):
            # localfile should be an xml configuration
            print(("{}:".format(localfile)))
            tree = etree.parse(localfile, parser)
            for node in tree.xpath("//*[./Password/text() != '']"):
                path = get_obj_path(node)
                remotefile = node.find("Filename").text
                password = node.find("Password").text
                print(('\tXPATH: {}\n\t\tFILENAME: {}\n\t\tPASSWORD: {}\n'.format(path, remotefile, password)))
                rows.append(",".join((localfile, path, remotefile, password)))

    with open(out_file, "wb") as fp:
        for row in rows:
            fp.write("{}\n".format(row))

    print(("Wrote CSV to: {}".format(out_file)))

if __name__ == "__main__":
    cli = Cli(main=main)
    try:
        cli.run()
    except SystemExit:
        pass
    except:
        make_logger("error").exception("Sorry, an unhandled exception occurred")
        raise
