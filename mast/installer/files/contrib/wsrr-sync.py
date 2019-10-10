from mast.datapower import datapower
from mast.logging import make_logger
from mast.cli import Cli

def main(appliances=[],
         credentials=[],
         domains=[],
         no_check_hostname=False,
         timeout=120,
    ):
    logger = make_logger("session_mon")
    check_hostname = not no_check_hostname

    env = datapower.Environment(
        appliances,
        credentials,
        timeout,
        check_hostname=check_hostname)
    for appliance in env.appliances:
        print((appliance.hostname))
        _domains = domains
        if "all-domains" in domains:
            _domains = appliance.domains
        for domain in _domains:
            print(("\t{}".format(domain)))
            config = appliance.get_config(
                _class="WSRRSubscription",
                domain=domain,
                persisted=False,
            )
            objs = config.xml.findall(datapower.CONFIG_XPATH)
            if not objs:
                continue
            for obj in objs:
                print(("\t\t{}".format(obj.get("name"))))
                resp = appliance.WsrrSynchronize(domain=domain, WSRRSubscription=obj.get("name"))
                print(("\t\t\t" + "\n\t\t\t{}".join(resp.xml.find(".//{http://www.datapower.com/schemas/management}result").itertext())))

if __name__ == "__main__":
    cli = Cli(main=main)
    try:
        cli.run()
    except SystemExit:
        pass
    except:
        make_logger("error").exception("An unhandled exception occurred")
        raise
