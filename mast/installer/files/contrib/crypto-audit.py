# -*- coding: utf-8 -*-
import os
import openpyxl
import pandas as pd
from mast.cli import Cli
from mast.datapower import datapower
from mast.logging import make_logger

default_out_file = os.path.join(os.environ["MAST_HOME"],
                                "tmp",
                                "cert-audit.xlsx")


def main(appliances=[],
         credentials=[],
         timeout=120,
         no_check_hostname=False,
         out_file=default_out_file):
    """Perform a crypto-audit on the specified appliances"""
    # Get a filestore of cert:, pubcert: and sharedcert: in the default
    # domain


if __name__ == "__main__":
    cli = Cli(main=main, description=main.__doc__)
    try:
        cli.run()
    except SystemExit:
        pass
    except:
        make_logger("error").exception()
        raise
