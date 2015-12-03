import mast.cli
import mast.config
import mast.cron
import mast.daemon
import mast.datapower.accounts
import mast.datapower.backups
import mast.datapower.datapower
import mast.datapower.deploy
import mast.datapower.deployment
import mast.datapower.developer
import mast.datapower.network
import mast.datapower.ssh
import mast.datapower.status
import mast.datapower.system
import mast.datapower.web
import mast.hashes
import mast.logging
import mast.plugins
import mast.plugin_utils
import mast.pprint
import mast.timestamp
import mast.xor

import os
import inspect
import textwrap
import markdown
from collections import OrderedDict
from markdown.extensions.toc import TocExtension

class LastUpdatedOrderedDict(OrderedDict):
    'Store items in the order the keys were last added'

    def __setitem__(self, key, value):
        if key in self:
            del self[key]
        OrderedDict.__setitem__(self, key, value)

css = """
<!DOCTYPE html>
<html>
    <head>
        <style>
            .codehilite .hll { background-color: #ffffcc }
            .codehilite  { background: #f8f8f8; }
            .codehilite .c { color: #408080; font-style: italic } /* Comment */
            .codehilite .err { border: 1px solid #FF0000 } /* Error */
            .codehilite .k { color: #008000; font-weight: bold } /* Keyword */
            .codehilite .o { color: #666666 } /* Operator */
            .codehilite .cm { color: #408080; font-style: italic } /* Comment.Multiline */
            .codehilite .cp { color: #BC7A00 } /* Comment.Preproc */
            .codehilite .c1 { color: #408080; font-style: italic } /* Comment.Single */
            .codehilite .cs { color: #408080; font-style: italic } /* Comment.Special */
            .codehilite .gd { color: #A00000 } /* Generic.Deleted */
            .codehilite .ge { font-style: italic } /* Generic.Emph */
            .codehilite .gr { color: #FF0000 } /* Generic.Error */
            .codehilite .gh { color: #000080; font-weight: bold } /* Generic.Heading */
            .codehilite .gi { color: #00A000 } /* Generic.Inserted */
            .codehilite .go { color: #808080 } /* Generic.Output */
            .codehilite .gp { color: #000080; font-weight: bold } /* Generic.Prompt */
            .codehilite .gs { font-weight: bold } /* Generic.Strong */
            .codehilite .gu { color: #800080; font-weight: bold } /* Generic.Subheading */
            .codehilite .gt { color: #0040D0 } /* Generic.Traceback */
            .codehilite .kc { color: #008000; font-weight: bold } /* Keyword.Constant */
            .codehilite .kd { color: #008000; font-weight: bold } /* Keyword.Declaration */
            .codehilite .kn { color: #008000; font-weight: bold } /* Keyword.Namespace */
            .codehilite .kp { color: #008000 } /* Keyword.Pseudo */
            .codehilite .kr { color: #008000; font-weight: bold } /* Keyword.Reserved */
            .codehilite .kt { color: #B00040 } /* Keyword.Type */
            .codehilite .m { color: #666666 } /* Literal.Number */
            .codehilite .s { color: #BA2121 } /* Literal.String */
            .codehilite .na { color: #7D9029 } /* Name.Attribute */
            .codehilite .nb { color: #008000 } /* Name.Builtin */
            .codehilite .nc { color: #0000FF; font-weight: bold } /* Name.Class */
            .codehilite .no { color: #880000 } /* Name.Constant */
            .codehilite .nd { color: #AA22FF } /* Name.Decorator */
            .codehilite .ni { color: #999999; font-weight: bold } /* Name.Entity */
            .codehilite .ne { color: #D2413A; font-weight: bold } /* Name.Exception */
            .codehilite .nf { color: #0000FF } /* Name.Function */
            .codehilite .nl { color: #A0A000 } /* Name.Label */
            .codehilite .nn { color: #0000FF; font-weight: bold } /* Name.Namespace */
            .codehilite .nt { color: #008000; font-weight: bold } /* Name.Tag */
            .codehilite .nv { color: #19177C } /* Name.Variable */
            .codehilite .ow { color: #AA22FF; font-weight: bold } /* Operator.Word */
            .codehilite .w { color: #bbbbbb } /* Text.Whitespace */
            .codehilite .mf { color: #666666 } /* Literal.Number.Float */
            .codehilite .mh { color: #666666 } /* Literal.Number.Hex */
            .codehilite .mi { color: #666666 } /* Literal.Number.Integer */
            .codehilite .mo { color: #666666 } /* Literal.Number.Oct */
            .codehilite .sb { color: #BA2121 } /* Literal.String.Backtick */
            .codehilite .sc { color: #BA2121 } /* Literal.String.Char */
            .codehilite .sd { color: #BA2121; font-style: italic } /* Literal.String.Doc */
            .codehilite .s2 { color: #BA2121 } /* Literal.String.Double */
            .codehilite .se { color: #BB6622; font-weight: bold } /* Literal.String.Escape */
            .codehilite .sh { color: #BA2121 } /* Literal.String.Heredoc */
            .codehilite .si { color: #BB6688; font-weight: bold } /* Literal.String.Interpol */
            .codehilite .sx { color: #008000 } /* Literal.String.Other */
            .codehilite .sr { color: #BB6688 } /* Literal.String.Regex */
            .codehilite .s1 { color: #BA2121 } /* Literal.String.Single */
            .codehilite .ss { color: #19177C } /* Literal.String.Symbol */
            .codehilite .bp { color: #008000 } /* Name.Builtin.Pseudo */
            .codehilite .vc { color: #19177C } /* Name.Variable.Class */
            .codehilite .vg { color: #19177C } /* Name.Variable.Global */
            .codehilite .vi { color: #19177C } /* Name.Variable.Instance */
            .codehilite .il { color: #666666 } /* Literal.Number.Integer.Long */
        </style>
    </head>
    <body>
"""

api_modules = LastUpdatedOrderedDict([
    (mast.cli, LastUpdatedOrderedDict()),
    (mast.config, LastUpdatedOrderedDict()),
    (mast.cron, LastUpdatedOrderedDict()),
    (mast.daemon, LastUpdatedOrderedDict()),
    (mast.datapower.datapower, LastUpdatedOrderedDict()),
    (mast.datapower.web, LastUpdatedOrderedDict()),
    (mast.hashes, LastUpdatedOrderedDict()),
    (mast.logging, LastUpdatedOrderedDict()),
    (mast.plugins, LastUpdatedOrderedDict()),
    (mast.plugin_utils, LastUpdatedOrderedDict()),
    (mast.pprint, LastUpdatedOrderedDict()),
    (mast.timestamp, LastUpdatedOrderedDict()),
    (mast.xor, LastUpdatedOrderedDict())
])

user_modules = OrderedDict([
    (mast.datapower.accounts, LastUpdatedOrderedDict()),
    (mast.datapower.backups, LastUpdatedOrderedDict()),
    (mast.datapower.deploy, LastUpdatedOrderedDict()),
    (mast.datapower.deployment, LastUpdatedOrderedDict()),
    (mast.datapower.developer, LastUpdatedOrderedDict()),
    (mast.datapower.network, LastUpdatedOrderedDict()),
    (mast.datapower.ssh, LastUpdatedOrderedDict()),
    (mast.datapower.status, LastUpdatedOrderedDict()),
    (mast.datapower.system, LastUpdatedOrderedDict())
 ])

def get_objects(modules):
    for module in dict(modules):
        functions = inspect.getmembers(module, inspect.isfunction)
        functions = filter(
            lambda x: not x[0].startswith("_"),
            functions)
        functions = filter(
            lambda x: module.__name__ in x[1].__module__,
            functions)
        modules[module]["functions"] = functions

        classes = inspect.getmembers(module, inspect.isclass)
        classes = filter(
            lambda x: not x[0].startswith("_"),
            classes)
        classes = filter(
            lambda x: module.__name__ in x[1].__module__,
            classes)
        if classes:
            modules[module]["classes"] = LastUpdatedOrderedDict()
        for cls in classes:
            methods = inspect.getmembers(cls[1], inspect.ismethod)
            methods = filter(
                lambda x: module.__name__ in x[1].__module__,
                methods)
            methods = filter(
                lambda x: hasattr(x[1], "__doc__") or x[0].startswith("_"),
                methods)
            if methods:
                modules[module]["classes"][cls] = methods
    return modules


def escape(string):
    return string.replace("_", "\_")

def generate_markdown(objects):
    md = ""
    for k, v in objects.items():
        # Module names
        md += "\n## {}\n".format(escape(k.__name__))
        if k.__doc__:
            md += "\n\n{}\n".format(textwrap.dedent(k.__doc__))
        else:
            md += "\n\nNo module level documentation\n"
        for _k, _v in v.items():
            # _k will either be functions or options
            md += "\n### {}\n".format(_k)
            if _k == "functions":
                for item in _v:
                    # Functions
                    md += "\n#### {}\n".format(escape(item[0]))
                    if item[1].__doc__:
                        md += "\n\n{}\n".format(
                            textwrap.dedent(item[1].__doc__))
                    else:
                        md += "\n\nNo documentation available for this function!\n"
            elif _k == "classes":
                for __k, __v in _v.items():
                    # class name
                    md += "\n#### {}\n".format(escape(__k[0]))
                    if __k[1].__doc__:
                        # Class level docstrings
                        md += "\n\n{}\n".format(textwrap.dedent(__k[1].__doc__))
                    else:
                        md += "\n\nNo documentation available for this class!\n"
                    for method in __v:
                        # Method names and docstrings
                        md += "\n##### {}\n".format(escape(method[0]))
                        if method[1].__doc__:
                            md += "\n\n{}\n".format(textwrap.dedent(method[1].__doc__))
                        else:
                            md += "\n\nNo documentation available for this method!\n"
    return md

def main(out_dir="tmp"):
    api_objects = get_objects(api_modules)
    api_md = generate_markdown(api_objects)
    api_md = "{}<h1>MAST Manual - API Documentation v 2.1.0</h1>\n\n[TOC]\n\n{}</body></html>".format(
        css, api_md)

    user_objects = get_objects(user_modules)
    user_md = generate_markdown(user_objects)
    user_md = "{}<h1>MAST Manual - User Documentation v 2.1.0</h1>\n\n[TOC]\n\n{}</body></html>".format(
        css, user_md)

    filename = os.path.join(out_dir, "APIDocs.html")
    with open(filename, "w") as fout:
        fout.write(markdown.markdown(api_md, extensions=[TocExtension(title="Table of Contents"), "markdown.extensions.codehilite"]))

    filename = os.path.join(out_dir, "UserDocs.html")
    with open(filename, "w") as fout:
        fout.write(markdown.markdown(user_md, extensions=[TocExtension(title="Table of Contents"), "markdown.extensions.codehilite"]))

# Module level docstrings
#   should only contain '###' and above
# Function level docstrings
#   should only contain '#####' and above
# Class level docstrings
#   should only contain '#####' and above
# Method level docstrings
#   should only contain '######' and above
#
# Headings (ie "#" * n) should only be used for sections
# not for comments within docstrings

if __name__ == "__main__":
    cli = mast.cli.Cli(main=main)
    cli.run()
