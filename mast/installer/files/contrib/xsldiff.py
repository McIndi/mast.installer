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

XPATHS = {
    '/*/*[local-name()="import"]': ['href'],
    '/*/*[local-name()="include"]': ['href'],
    '/*/*[local-name()="output"]': [
        'method',
        'version',
        'encoding',
        'omit-xml-declaration',
        'standalone',
        'doctype-public',
        'doctype-system',
        'cdata-section-elements',
        'indent',
        'media-type',
    ],
    '/*/*[local-name()="attribute-set"]': ['name'],
    '/*/*[local-name()="param"]': ['name'],
    '/*/*[local-name()="variable"]': [
        'name',
        'select',
    ],
    '/*/*[local-name()="template"]': [
        'name',
        'match',
        'priority',
        'mode',
    ],
    '/*/*[local-name()="function"]': ['name'],
}

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
        xsl_globs=[],
        out_dir="tmp",
        wrapcolumn=80,
        tabsize=4,
        no_only_differences=False,
        no_same_filenames=False,
    ):
    only_differences = not no_only_differences
    same_filenames = not no_same_filenames
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)
    parser = etree.XMLParser(
        remove_blank_text=True,
        strip_cdata=False,
    )
    differ = difflib.HtmlDiff(wrapcolumn=wrapcolumn, tabsize=tabsize)
    # Get list of filenames
    # Start with a set for uniqueness
    filenames = set()
    for pattern in xsl_globs:
        for filename in glob(pattern):
            filenames.add(os.path.abspath(filename))
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

    # Pretty print for consistency
    for filename in filenames:
        tree = etree.parse(filename, parser)
        with open(filename, "w") as fp:
            fp.write(etree.tostring(tree, pretty_print=True))

    for filename in _filenames:
        print(("{} {}".format(get_sha256(os.path.join(common_prefix, filename)), filename)))

    # Gather top level nodes and compare
    for index, (left_filename, right_filename) in enumerate(combinations(filenames, 2)):
        if same_filenames and os.path.basename(left_filename) != os.path.basename(right_filename):
            continue
        if get_sha256(left_filename) == get_sha256(right_filename):
            continue
        print(("{} -> {}".format(left_filename, right_filename)))
        html_rows = OrderedDict(
            (
                ('/*/*[local-name()="import"]', []),
                ('/*/*[local-name()="include"]', []),
                ('/*/*[local-name()="output"]', []),
                ('/*/*[local-name()="attribute-set"]', []),
                ('/*/*[local-name()="param"]', []),
                ('/*/*[local-name()="variable"]', []),
                ('/*/*[local-name()="template"]', []),
                ('/*/*[local-name()="function"]', []),
            )
        )
        left_tree = etree.parse(left_filename, parser)
        right_tree = etree.parse(right_filename, parser)
        left_nodes = {}
        right_nodes = {}
        for xpath, identifiers in list(XPATHS.items()):
            left_nodes[xpath] = {}
            right_nodes[xpath] = {}
            for node in left_tree.xpath(xpath):
                identity = tuple(node.get(identifier) for identifier in identifiers)
                left_nodes[xpath][identity] = etree.tostring(node, pretty_print=True)
            for node in right_tree.xpath(xpath):
                identity = tuple(node.get(identifier) for identifier in identifiers)
                right_nodes[xpath][identity] = etree.tostring(node, pretty_print=True)
        for xpath, identifiers in list(left_nodes.items()):
            for identifier, left_text in list(identifiers.items()):
                if identifier in right_nodes[xpath]:
                    # Item exists in both left and right
                    right_text = right_nodes[xpath][identifier]
                    if only_differences and hashlib.sha256(left_text).hexdigest() == hashlib.sha256(right_text).hexdigest():
                        pass
                    else:
                        html_rows[xpath].append(
                            TABLE_ROW.format(
                                differ.make_table(
                                    left_text.splitlines(),
                                    right_text.splitlines(),
                                    left_filename,
                                    right_filename,
                                )
                            )
                        )
                else:
                    # Exists on left but not on right
                    rside = "{}\n".format(" "*(wrapcolumn-1)) * len(left_text.splitlines())
                    rside = rside.splitlines()
                    html_rows[xpath].append(
                        TABLE_ROW.format(
                            differ.make_table(
                                left_text.splitlines(),
                                rside,
                                left_filename,
                                right_filename,
                            )
                        )
                    )
        for xpath, identifiers in list(right_nodes.items()):
            for identifier, right_text in list(identifiers.items()):
                if identifier not in left_nodes[xpath]:
                    lside = "{}\n".format(" "*(wrapcolumn-1)) * len(right_text.splitlines())
                    lside = lside.splitlines()
                    html_rows[xpath].append(
                        TABLE_ROW.format(
                            differ.make_table(
                                lside,
                                right_text.splitlines(),
                                left_filename,
                                right_filename,
                            )
                        )
                    )

        left_root = left_tree.getroot()
        for child in left_root.iterchildren():
            left_root.remove(child)
        left_root = etree.tostring(left_root, pretty_print=True)

        right_root = right_tree.getroot()
        for child in right_root.iterchildren():
            right_root.remove(child)
        right_root = etree.tostring(right_root, pretty_print=True)

        if only_differences and hashlib.sha256(left_root).hexdigest() == hashlib.sha256(right_root).hexdigest():
            pass
        else:
            html_rows[xpath].insert(
                0,
                TABLE_ROW.format(
                    differ.make_table(
                        left_root.splitlines(),
                        right_root.splitlines(),
                        left_filename,
                        right_filename,
                    )
                )
            )


        if same_filenames:
            diff_filename = "{}-{}-vs-{}-{}.html".format(
                index,
                "_".join(list(OrderedDict.fromkeys([x for x in left_filename.split(os.path.sep) if x not in right_filename.split(os.path.sep)]))),
                "_".join(list(OrderedDict.fromkeys([x for x in right_filename.split(os.path.sep) if x not in left_filename.split(os.path.sep)]))),
                os.path.basename(left_filename),
            )
        else:
            diff_filename = "{}-{}-vs-{}.html".format(
                index,
                "_".join(list(OrderedDict.fromkeys([x for x in left_filename.split(os.path.sep) if x not in right_filename.split(os.path.sep)]))),
                "_".join(list(OrderedDict.fromkeys([x for x in right_filename.split(os.path.sep) if x not in left_filename.split(os.path.sep)]))),
            )
        diff_filename = os.path.join(
            out_dir,
            diff_filename,
        )
        _html_rows = []
        for xpath, rows in list(html_rows.items()):
            _html_rows.extend(rows)
        with open(diff_filename, "wb") as fp:
            fp.write(
                HTML_TABLE.format("".join(_html_rows))
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
