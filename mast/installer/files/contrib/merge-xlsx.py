# -*- coding: utf-8 -*-
from mast.logging import make_logger
from mast.cli import Cli
import pandas as pd
import os

__version__ = "{}-0".format(os.environ["MAST_VERSION"])

def main(left_file="",
         right_file="",
         out_file="",
         on=[],
         how="left"):
    """given two xlsx (excel) workbooks, each containing one worksheet,
join the two worksheets and output a new workbook.

Parameters:

* `-l, --left-file`: The workbook which contains the worksheet
to consider the "left" table
* `-r, --right-file`: The workbook which contains the worksheet
to consider the "right" table
* `-o, --out-file`: The file to output the "joined" tables to
* `-O, --on`: A (space-seperated) list of column names to join on
* `-H, --how`: how to join the two tables, must be one of "left",
"right", "outer" or "inner"

For more information on joining tables please see the
[pandas dataframe merge documentation](http://pandas.pydata.org/pandas-docs/version/0.17.1/generated/pandas.DataFrame.merge.html)
    """
    left = pd.read_excel(left_file)
    right = pd.read_excel(right_file)
    new = pd.merge(left, right, on=on, how=how)
    print "SAVING {}".format(out_file)
    new.to_excel(out_file, index=False)


if __name__ == "__main__":
    cli = Cli(main=main, description=main.__doc__)
    try:
        cli.run()
    except SystemExit:
        pass
    except:
        make_logger("error").exception("An unhandled exception has occurred")
        raise
