# -*- coding: utf-8 -*-
"""
merge_logger_info.py

This  is a very specialized script. It takes two excel workbooks which
should contain exacly one worksheet each. This worksheet should contain
the LogTarget configuration in the one and LogTargetStatus. You can generate
these workbooks with the following commands:

$ ./mast usrbin/getconfig.py -a $HOSTNAMES -c $CREDENTIALS -d all-domains -o LogTarget
$ ./mast usrbin/getstatus.py -a $HOSTNAMES -c $CREDENTIALS -d all-domains -p LogTargetStatus

Once those commands are run you should have two files and you can use this
script to perform the equivalent of a LEFT JOIN on the two worksheets
thereby generating an excel workbook with one worksheet containing the
combined output from the two previous commands.
"""
import os
import sys
from mast.cli import Cli
from mast.logging import make_logger
import pandas as pd

def main(config_xlsx="",
         status_xlsx="",
         out_file=""):
    config = pd.read_excel(config_xlsx)
    status = pd.read_excel(status_xlsx)
    status.rename(
        columns={"hostname": "appliance", "LogTarget": "Object Name"},
        inplace=True
    )
    new = pd.merge(status, config, on=["appliance", "domain", "Object Name"])
    new.to_excel(out_file)


if __name__ == "__main__":
    try:
        cli = Cli(main=main)
        cli.run()
    except SystemExit:
        pass
    except:
        make_logger("error").exception(
            "Sorry, an unhandled exception occurred while executing command")
        raise
