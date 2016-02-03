# -*- coding: utf-8 -*-
from mast.datapower import datapower
import os
from time import sleep
from functools import partial
from mast.datapower.datapower import Environment
import sys
from mast.logging import make_logger
from mast.cli import Cli
from mast.timestamp import Timestamp

# #########################
# TODO:
#
# New Features:
#
# 1. column filter
# 2. optional concurency
# 3. column sort
# 4. Integrate with MAST 2.0.0
# 5. Multiple status provider
#
# #########################

logger = make_logger("mast.statmon")

clear = partial(os.system, 'cls' if os.name == 'nt' else 'clear')


def recurse_status(prefix, elem, row, header_row):
    for child in elem.findall(".//*"):
        logger.info("Found child {}".format(child.tag))
        if child.tag not in header_row:
            logger.debug("Appending {} to header row".format(child.tag))
            header_row.append(child.tag)
        if len(child):
            _prefix = "{}/{}".format(prefix, child.tag)
            logger.info("child {} has children, recursing...".format(_prefix))
            recurse_status(_prefix, child, row, header_row)
        else:
            logger.info("Adding {} -> {}".format(child.tag, child.text))
            row.insert(header_row.index(child.tag), child.text)


def display_rows(header_row, rows, grep, provider):
    _format_string = ""
    for index, field in enumerate(header_row):
        _ = [field] + [str(x[index]) for x in rows]
        length = len(max(_, key=len)) + 3
        _format_string += "{%s: <%s}" % (index, length)
    clear()
    print Timestamp()
    print provider
    print "\n", _format_string.format(*header_row)
    print '-' * len(_format_string.format(*header_row))
    for row in rows:
        if grep:
            if grep in _format_string.format(*row):
                print _format_string.format(*row)
        else:
            print _format_string.format(*row)


def main(appliances=[],
         credentials=[],
         timeout=120,
         no_check_hostname=False,
         provider="",
         domains=[],
         interval=0,
         grep=""):

    if not provider:
        msg = "provider must be provided"
        logger.error(msg)
        print msg
        sys.exit(1)

    check_hostname = not no_check_hostname
    env = Environment(
        appliances,
        credentials,
        timeout,
        check_hostname=check_hostname)
    if interval:
        while True:
            print_table(env, provider, domains, grep)
            sleep(interval)
    else:
        print_table(env, provider, domains, grep)


def print_table(env, provider, domains, grep):
    header_row = ["hostname"]

    rows = []
    for appliance in env.appliances:
        _domains = domains
        if "all-domains" in domains:
            _domains = appliance.domains

        for domain in _domains:
            status = appliance.get_status(provider, domain=domain)
            for node in status.xml.findall(datapower.STATUS_XPATH):
                row = [appliance.hostname]
                recurse_status("", node, row, header_row)
                rows.append(row)
    display_rows(header_row, rows, grep, provider)

if __name__ == "__main__":
    try:
        cli = Cli(main=main, description=__doc__)
        cli.run()
    except KeyboardInterrupt:
        sys.exit(0)
    except SystemExit:
        raise
    except:
        make_logger("error").exception(
            "An unhandled exception occurred during execution")
        raise
