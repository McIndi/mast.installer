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
        msg = "Generating Error report on {}".format(appliance.hostname)
        print msg
        appliance.log_info(msg)
        resp = appliance.ErrorReport()
        if resp:
            msg = "Successfully generated error report on {}".format(
                appliance.hostname)
            print "\t", msg
            appliance.log_info(msg)
        else:
            msg = "An error occurred generating error report on {}: \n{}".format(
                appliance.hostname, resp)
            print "\t", msg
            appliance.log_error(msg)


if __name__ == "__main__":
    cli = Cli(main=main)
    try:
        cli.run()
    except SystemExit:
        pass
    except:
        make_logger("error").exception("An unhandled exception occurred")
        raise
