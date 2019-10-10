import os
import atexit
from mast.cli import Cli
from glob import glob
from mast.logging import make_logger
from mast.datapower.datapower import CONFIG_XPATH
from collections import defaultdict
from lxml import etree

class DPObject(object):
    def __init__(self, klass, name):
        self.klass = klass
        self.name = name

    def __repr__(self):
        return "{} {}".format(self.klass, self.name)

def main(
        config_globs=[],
        out_file=None,
    ):
    if not out_file:
        out_file = sys.stdout
    else:
        out_file = open(out_file, "w")
        atexit.register(out_file.close)
    for pattern in config_globs:
        for filename in glob(pattern):
            # filename should be the xml configuration of the entire domain
            # Get a list of all objects
            objects = []
            referenced_objects = defaultdict(list)
            config = etree.parse(filename)
            for obj in config.findall(CONFIG_XPATH):
                objects.append(DPObject(obj.tag, obj.get("name")))

            dirname = os.path.dirname(filename)
            # Filter out objects directly referenced in the xcfg
            xcfg_pattern = os.path.join(dirname, "*.xcfg")
            for _filename in glob(xcfg_pattern):
                xcfg = etree.parse(_filename)
                for _obj in xcfg.xpath("/datapower-configuration/configuration/*"):
                    klass, name = _obj.tag, _obj.get("name")
                    objects = list(filter(
                        lambda obj: not (obj.klass == klass and obj.name == name),
                        objects,
                    ))

            # Filter out some things we are not interested in
            objects = list(filter(
                lambda obj: obj.klass.lower() != "loglabel",
                objects,
            ))
            objects = list(filter(
                lambda obj: obj.name.lower() != "default",
                objects,
            ))
            objects = list(filter(
                lambda obj: obj.name.lower() != "test",
                objects,
            ))
            objects = list(filter(
                lambda obj: obj.name.lower() != "all",
                objects,
            ))

            dirname = os.path.join(dirname, "files")
            for root, dirs, files in os.walk(dirname):
                for _filename in files:
                    print(_filename)
                    _filename = os.path.join(root, _filename)
                    with open(_filename, "rb") as fp:
                        for lineno, line in enumerate(fp):
                            for obj in objects:
                                if obj.klass in line or obj.name in line:
                                    referenced_objects[obj].append((_filename, lineno))
            print(referenced_objects)
            out_file.write("{}\n".format(filename))
            for obj, refs in list(referenced_objects.items()):
                out_file.write("\n\t{}\n".format(obj))
                for ref in refs:
                    out_file.write("\t\t{0} {1}\n".format(*ref))

if __name__ == "__main__":
    cli = Cli(main=main)
    try:
        cli.run()
    except SystemExit:
        pass
    except:
        make_logger("error").exception("Sorry, an unhandled exception occurred")
        raise
