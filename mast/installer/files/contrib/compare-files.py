from itertools import combinations
from mast.logging import make_logger
from mast.cli import Cli
from mast.hashes import get_sha512
import difflib
import glob
import os

def main(pattern="", out_dir="", wrapcolumn=80, tabsize=4):
    diff = difflib.HtmlDiff(
        tabsize=tabsize,
        wrapcolumn=wrapcolumn,
        linejunk=None,
        charjunk=difflib.IS_CHARACTER_JUNK
    )
    filenames = []
    for filename in glob.glob(pattern):
        filenames.append(os.path.abspath(filename))
    for combination in combinations(filenames, 2):
        from_file, to_file = combination
        if get_sha512(from_file) == get_sha512(to_file):
            continue
        with open(from_file, "r") as fp:
            from_lines = fp.readlines()
        with open(to_file, "r") as fp:
            to_lines = fp.readlines()

        diff_filename = "{}-vs-{}.html".format(
            "_".join([x for x in from_file.split(os.path.sep) if x not in to_file.split(os.path.sep)]),
            "_".join([x for x in to_file.split(os.path.sep) if x not in from_file.split(os.path.sep)]),
        )
        diff_filename = os.path.join(
            out_dir,
            diff_filename,
        )
        with open(diff_filename, "wb") as fp:
            fp.write(
                diff.make_file(
                    from_lines,
                    to_lines,
                    from_file,
                    to_file,
                )
            )



if __name__ == "__main__":
    cli = Cli(main=main)
    try:
        cli.run()
    except SystemExit:
        pass
    except:
        make_logger("error").exception("An unhandled error has occurred")
        raise
