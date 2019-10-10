import sys
from lxml import etree
from mast.cli import Cli
from mast.logging import make_logger
from itertools import groupby
from collections import OrderedDict
from glob import glob

def sort_children(node, sort_attribute):
    children = node.xpath("./*")
    children =  sorted(children, key=lambda child: child.tag)
    groups = groupby(children, key=lambda child: child.tag)
    groups = dict((x, list(y)) for x, y in groups)
    for k in sorted(groups.keys()):
        for child in sorted(groups[k], key=lambda child: child.get("name")):
            if len(child):
                sort_children(child, sort_attribute)
            _attrib = OrderedDict((k, v) for k, v in sorted(list(child.attrib.items()), key=lambda n: n[0]))
            node.remove(child)
            child.attrib.clear()
            child.attrib.update(_attrib)
            node.append(child)


def main(xml_file_glob="", sort_attribute="name"):
    """sort xml nodes and attributes in alphabetical order and
    normalize whitespace. Use sort-attribute (default "name") to define
    the attribute to sort by within elements with the same tag name.
    """
    parser = etree.XMLParser(remove_blank_text=True)
    for filename in glob(xml_file_glob):
        print(filename)
        tree = etree.parse(filename, parser).getroot()
        sort_children(tree, sort_attribute)

        with open(filename, "wb") as fp:
            fp.write(etree.tostring(tree, pretty_print=True))

if __name__ == "__main__":
    cli = Cli(main=main)
    try:
        cli.run()
    except SystemExit:
        pass
    except:
        make_logger("error").exception("an unhandled exception occurred.")
        raise
