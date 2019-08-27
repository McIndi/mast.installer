from glob import glob
from lxml import etree
from mast.cli import Cli

parser = etree.XMLParser(remove_blank_text=True)

def main(glob_pattern=""):
    for filename in glob(glob_pattern):
        print(filename)
        doc = etree.parse(filename, parser)
        for node in doc.xpath("./interface-data"):
            doc.getroot().remove(node)
        for node in doc.xpath("./files"):
            doc.getroot().remove(node)
        for node in doc.xpath("./export-details"):
            doc.getroot().remove(node)
        for node in doc.xpath(".//*"):
            if "intrinsic" in node.attrib:
                del node.attrib["intrinsic"]
            if "read-only" in node.attrib:
                del node.attrib["read-only"]
        with open("{}".format(filename), "w") as fout:
            fout.write(etree.tostring(doc, pretty_print=True))
            

if __name__ == "__main__":
    cli = Cli(main=main)
    try:
        cli.run()
    except SystemExit:
        pass
    except:
        raise
