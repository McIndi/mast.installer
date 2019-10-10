
import os
import atexit
from mast.cli import Cli
from mast.logging import make_logger
from mast.datapower import datapower

def main(appliances=[],
         credentials=[],
         timeout=120,
         EthernetInterface="",
         add=[],
         remove=[],
         save_config=False):
    """
    _Script_: `contrib/ssh-add-static-route.py`

    DESCRIPTION:

    Adds or removes multiple static routes to an EthernetInterface.

    USAGE:

    To add two static routes and remove two static routes from two appliances,
    this is the form you should use:

    ```
    $ mast contrib/ssh-routes.py --appliances APPL_1 --appliances APPL_2 --credentials user:pass --EthernetInterface INT_NAME --add "xxx.xxx.xxx.xxx/xx xxx.xxx.xxx.xxx x" --add "xxx.xxx.xxx.xxx/xx xxx.xxx.xxx.xxx x" --remove "xxx.xxx.xxx.xxx/xx xxx.xxx.xxx.xxx x" --remove "xxx.xxx.xxx.xxx/xx xxx.xxx.xxx.xxx x"
    ```

    RETURNS

    PARAMETERS:

    * `-a, --appliances`: The hostname(s), ip address(es), environment name(s)
    or alias(es) of the appliances you would like to affect. For details
    on configuring environments please see the comments in
    `environments.conf` located in `$MAST_HOME/etc/default`. For details
    on configuring aliases, please see the comments in `hosts.conf` located in
    `$MAST_HOME/etc/default`. To pass multiple arguments to this parameter,
    use multiple entries of the form `[-a appliance1 [-a appliance2...]]`
    * `-c, --credentials`: The credentials to use for authenticating to the
    appliances. Should be either one set to use for all appliances
    or one set for each appliance. Credentials should be in the form
    `username:password`. To pass multiple credentials to this parameter, use
    multiple entries of the form `[-c credential1 [-c credential2...]]`.
    When referencing multiple appliances with multiple credentials,
    there must be a one-to-one correspondence of credentials to appliances:
    `[-a appliance1 [-a appliance2...]] [-c credential1 [-c credential2...]]`
    If you would prefer to not use plain-text passwords,
    you can use the output of `$ mast-system xor <username:password>`.
    * `-t, --timeout`: The timeout in seconds to wait for a response from
    an appliance for any single request. __NOTE__ Program execution may
    halt if a timeout is reached.
    * `-E, --EthernetInterface`: The name of the EthernetInterface to which
    to add the static route.
    * `-A, --add`: The static route(s) to add, should be in
    the form of "ip/cidr gateway metric" Where ip/cidr is the destination
    IP address and CIDR mask, gateway is the next-hop router's IP Address
    and metric is the numerical weighting of the static route. Multiple
    static routes can be added by specifying `--add` with proper
    arguments multiple times.
    * `-r, --remove`: The static route(s) to remove, should be in
    the form of "ip/cidr gateway metric" Where ip/cidr is the destination
    IP address and CIDR mask, gateway is the next-hop router's IP Address
    and metric is the numerical weighting of the static route. Multiple
    static routes can be removed by specifying `--remove` with
    proper arguments multiple times.
    * `-s, --save-config`: If specified, the configuration will be saved.

    **NOTE** static routes specified in `--del` and `--add` must contain
    spaces and so must be quoted
    """
    del_static_routes = [] if remove is None else remove
    add_static_routes = [] if add is None else add

    env = datapower.Environment(appliances,
                                credentials,
                                timeout=timeout)
    env.perform_action("ssh_connect", domain="default")
    atexit.register(env.perform_action, "ssh_disconnect")
    for appliance in env.appliances:
        issue_command = appliance.ssh_issue_command
        print((appliance.hostname, "\n"))
        print((issue_command("config")))
        print((issue_command("interface {}".format(EthernetInterface))))
        print((issue_command("show route")))
        for static_route in del_static_routes:
            print((issue_command("no ip route {}".format(static_route))))
        for static_route in add_static_routes:
            print((issue_command("ip route {}".format(static_route))))
        print((issue_command("exit")))
        if save_config:
            print((issue_command("write mem")))
            print((issue_command("y")))
        print((issue_command("show route")))
        print((issue_command("exit")))


if __name__ == "__main__":
    cli = Cli(main=main, description=main.__doc__)
    try:
        cli.run()
    except SystemExit:
        # Don't need logs when user asks for help
        pass
    except:
        make_logger("error").exception(
            "An exception ocurred during execution.")
        raise
