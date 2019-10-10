from mast.datapower import datapower
from mast.logging import make_logger
from mast.cli import Cli

def main(appliances=[],
         credentials=[],
         domains=[],
         no_check_hostname=False,
         timeout=120,
         object_class="",
         commands=[],
         dry_run=False,
         save_config=False,
    ):
    logger = make_logger("session_mon")
    check_hostname = not no_check_hostname

    env = datapower.Environment(
        appliances,
        credentials,
        timeout,
        check_hostname=check_hostname)
    for appliance in env.appliances:
        print(("{}\n================\n\n".format(appliance.hostname)))
        _domains = domains
        if "all-domains" in domains:
            _domains = appliance.domains
        _commands = []
        for domain in _domains:
            config = appliance.get_config(
                _class=object_class,
                domain=domain,
                persisted=False,
            )
            objs = config.xml.findall(datapower.CONFIG_XPATH)
            if not objs:
                continue
            _commands.append("switch domain {}".format(domain))
            _commands.append("co")
            for obj in objs:
                _commands.append("{} {}".format(object_class, obj.get("name")))
                for command in commands:
                    _commands.append(command)
                _commands.append("exit")
            if save_config:
                _commands.append("write mem")
            _commands.append("exit")
        if dry_run:
            for _command in _commands:
                print(_command)
        else:
            appliance.ssh_connect()
            for _command in _commands:
                print((appliance.ssh_issue_command(_command)))
            appliance.ssh_disconnect()




if __name__ == "__main__":
    cli = Cli(main=main)
    try:
        cli.run()
    except KeyboardInterrupt:
        pass
    except:
        make_logger("error").exception("An unhandled exception occurred")
        raise
