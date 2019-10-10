import os
import io
import sys
import difflib
import hashlib
from lxml import etree
from mast.cli import Cli
from mast.hashes import get_sha256
from mast.logging import make_logger
from itertools import groupby, combinations
from collections import OrderedDict, defaultdict
from glob import glob

remove_namespaces_xslt = '''<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
<xsl:output method="xml" indent="no"/>

<xsl:template match="/|comment()|processing-instruction()">
    <xsl:copy>
      <xsl:apply-templates/>
    </xsl:copy>
</xsl:template>

<xsl:template match="*">
    <xsl:element name="{local-name()}">
      <xsl:apply-templates select="@*|node()"/>
    </xsl:element>
</xsl:template>

<xsl:template match="@*">
    <xsl:attribute name="{local-name()}">
      <xsl:value-of select="."/>
    </xsl:attribute>
</xsl:template>
</xsl:stylesheet>
'''
remove_namespaces_xslt = etree.parse(io.BytesIO(str.encode(remove_namespaces_xslt)))
REMOVE_NAMESPACES = etree.XSLT(remove_namespaces_xslt)

def sort_children(node):
    children = node.xpath("./*")
    children =  sorted(children, key=lambda child: child.tag)
    groups = groupby(children, key=lambda child: child.tag)
    groups = dict((x, list(y)) for x, y in groups)
    for k in sorted(groups.keys()):
        for child in sorted(groups[k], key=lambda child: child.get("name")):
            if len(child):
                sort_children(child)
            _attrib = OrderedDict((k, v) for k, v in sorted(list(child.attrib.items()), key=lambda n: n[0]))
            node.remove(child)
            child.attrib.clear()
            child.attrib.update(_attrib)
            node.append(child)

def clean(tree):
    for node in tree.xpath("/datapower-configuration/export-details"):
        tree.remove(node)
    for node in tree.xpath("/datapower-configuration/interface-data"):
        tree.remove(node)
    for node in tree.xpath("/datapower-configuration/files"):
        tree.remove(node)
    for node in tree.xpath(".//*"):
        if "intrinsic" in node.attrib:
            del node.attrib["intrinsic"]
        if "read-only" in node.attrib:
            del node.attrib["read-only"]

def get_obj_path(node):
    return '/{}/{}[@name="{}"]'.format(
        "/".join(
            anc.tag for anc in reversed(list(node.iterancestors()))
        ),
        node.tag,
        node.get("name")
    )

HTML_TABLE = """
<html>
    <head>
        <style type="text/css">
        body {{width: 100%}}
        table.diff {{font-family:Courier; border:medium; width: 100%;}}
        .diff_header {{background-color:#e0e0e0}}
        td.diff_header {{text-align:right; width: auto;}}
        .diff_next {{background-color:#c0c0c0;}}
        .diff_add {{background-color:#aaffaa;}}
        .diff_chg {{background-color:#ffff77;}}
        .diff_sub {{background-color:#ffaaaa;}}
        </style>
    </head>
    <body>
        {}
    </body>
</html>
"""
TABLE_ROW = """
    <div style="width: 100%">
        {}
    </div>
"""

def main(
        xcfg_globs=[],
        out_dir="tmp",
        wrapcolumn=80,
        tabsize=4,
        no_only_differences=False,
        no_remove_namespaces=False,
    ):
    only_differences = not no_only_differences
    remove_namespaces = not no_remove_namespaces
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)
    parser = etree.XMLParser(
        remove_blank_text=True,
        strip_cdata=False,
    )
    differ = difflib.HtmlDiff(wrapcolumn=wrapcolumn, tabsize=tabsize)
    filenames = set()
    # Clean up xml documents
    for pattern in xcfg_globs:
        for filename in glob(pattern):
            filenames.add(os.path.abspath(filename))
            tree = etree.parse(filename, parser).getroot()
            if remove_namespaces:
                tree = REMOVE_NAMESPACES(tree).getroot()
            clean(tree)
            sort_children(tree)
            with open(filename, "wb") as fp:
                fp.write(etree.tostring(tree, pretty_print=True))
    # Cast to a list for order
    filenames = list(filenames)
    # sort by basename
    common_prefix = os.path.dirname(os.path.commonprefix(filenames))
    _filenames = list(map(
        lambda x: x.replace(common_prefix, ""),
        filenames,
    ))

    # remove leading path seperator
    _filenames = list(map(
        lambda x: x.lstrip(os.path.sep),
        _filenames,
    ))

    # Sort by dirname
    _filenames.sort(key=lambda p: p.split(os.path.sep))

    # sort by filename
    _filenames.sort(key=os.path.basename)

    for filename in _filenames:
        print(("{} {}".format(get_sha256(os.path.join(common_prefix, filename)), filename)))

    for index, (left_filename, right_filename) in enumerate(combinations(filenames, 2)):
        if get_sha256(left_filename) == get_sha256(right_filename):
            continue
        html_rows = []
        left_tree = etree.parse(left_filename, parser)
        left_config = left_tree.getroot().xpath("/datapower-configuration/configuration")[0]
        right_tree = etree.parse(right_filename, parser)
        right_config = right_tree.getroot().xpath("/datapower-configuration/configuration")[0]
        for lchild in left_config.iterchildren():
            lpath = get_obj_path(lchild)
            rchild = right_config.xpath(lpath)
            if not rchild:
                rside = "{}\n".format(" "*(wrapcolumn-1)) * len(etree.tostring(lchild, pretty_print=True).splitlines())
                rside = rside.splitlines()
                html_rows.append(
                    TABLE_ROW.format(
                        differ.make_table(
                            etree.tostring(lchild, pretty_print=True).splitlines(),
                            rside,
                            left_filename,
                            right_filename,
                        )
                    )
                )
            elif len(rchild) > 1:
                raise ValueError("ERROR: Path {} was expected to be unique but yielded {} results".format(lpath, len(rchild)))
            else:
                rchild = rchild[0]
                str_lchild = etree.tostring(lchild, pretty_print=True)
                str_rchild = etree.tostring(rchild, pretty_print=True)
                if only_differences and hashlib.sha256(str_lchild).hexdigest() == hashlib.sha256(str_rchild).hexdigest():
                    pass
                else:
                    html_rows.append(
                        TABLE_ROW.format(
                            differ.make_table(
                                str_lchild.splitlines(),
                                str_rchild.splitlines(),
                                left_filename,
                                right_filename,
                            )
                        )
                    )
        for rchild in right_config.iterchildren():
            rpath = get_obj_path(rchild)
            lchild = left_config.xpath(rpath)
            if not lchild:
                lside = "{}\n".format(" "*(wrapcolumn-1)) * len(etree.tostring(rchild, pretty_print=True).splitlines())
                lside = lside.splitlines()
                html_rows.append(
                    TABLE_ROW.format(
                        differ.make_table(
                            lside,
                            etree.tostring(rchild, pretty_print=True).splitlines(),
                            left_filename,
                            right_filename,
                        )
                    )
                )
        diff_filename = "{}-{}-vs-{}-{}.html".format(
            index,
            "_".join(list(OrderedDict.fromkeys([x for x in left_filename.split(os.path.sep) if x not in right_filename.split(os.path.sep)]))),
            "_".join(list(OrderedDict.fromkeys([x for x in right_filename.split(os.path.sep) if x not in left_filename.split(os.path.sep)]))),
            os.path.basename(left_filename),
        )
        diff_filename = os.path.join(
            out_dir,
            diff_filename,
        )
        with open(diff_filename, "wb") as fp:
            fp.write(
                HTML_TABLE.format("".join(html_rows))
            )


if __name__ == "__main__":
    cli = Cli(main=main)
    try:
        cli.run()
    except SystemExit:
        pass
    except:
        make_logger("error").exception("an unhandled exception occurred.")
        raise
