# -*- coding: utf-8 -*-
from mast.datapower import datapower
from mast.logging import make_logger
from mast.cli import Cli
from time import sleep, time


def main(appliances=[],
         credentials=[],
         timeout=120,
         no_check_hostname=False,
         delay=10,
         wait=1200):
    """Reboot appliances one-by-one waiting for the previous appliance to
    come back up before moving on to the next one.

    Arguments:

        appliances - The appliances to reboot

        credentials - The credentials to use to authenticate with

        timeout - The time (in seconds) to wait for any one response
        from the appliances

        delay - The time (in seconds) for the appliance to wait before
        rebooting

        no_check_hostname - specify to disable hostname verification

        wait - The time (in seconds) to wait for an appliance to come
        back up. An error will be raised if the appliance does not come
        back up and the script will stop."""
    logger = make_logger("reboot")
    check_hostname = not no_check_hostname
    env = datapower.Environment(
        appliances,
        credentials,
        timeout,
        check_hostname=check_hostname)
    for appliance in env.appliances:
        print "rebooting {}".format(appliance.hostname)
        kwargs = {"Mode": "reboot", "Delay": str(delay)}
        resp = appliance.Shutdown(**kwargs)
        msg = "\tOK" if resp else "\tFAILED"
        print msg
        sleep(delay)
        start = time()
        while True:
            sleep(5)
            if appliance.is_reachable():
                print "\tAppliance is back up, moving on"
                break
            if (time() - start) > wait:
                print "\tAppliace failed to respond within the specified time."
                print "Exiting"
                logger.error(
                    "{} failed to respond within the specified time".format(
                        appliance.hostname
                    )
                )
                sys.exit(-1)


if __name__ == "__main__":
    cli = Cli(main=main)
    try:
        cli.run()
    except SystemExit:
        pass
    except:
        msg = "Sorry, an unhandled exception occurred during execution"
        make_logger("error").exception(msg)
        raise
