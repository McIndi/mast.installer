# -*- coding: utf-8 -*-
from mast.cli import Cli
from mast.logging import make_logger
from mast.datapower import datapower


def main(appliances=[],
         credentials=[],
         timeout=120,
         no_check_hostname=False):
    check_hostname = not no_check_hostname
    env = datapower.Environment(appliances,
                                credentials,
                                timeout=timeout,
                                check_hostname=check_hostname)
    for appliance in env.appliances:
        print appliance.domains


if __name__ == "__main__":
    cli = Cli(main=main)
    try:
        cli.run()
    except SystemExit:
        pass
    except:
        make_logger("error").exception("An unhandled exception occurred.")
        raise
