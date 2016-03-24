"""
modify-config.py

POC for dynamically updating one or more attributes on groups of objects.
"""
from mast.datapower import datapower
from mast.logging import make_logger
from mast.cli import Cli


def main(appliances=[],
         credentials=[],
         timeout=120,
         no_check_hostname=False,
         domains=[],
         obj_class="",
         obj_name="",
         mods=[],
         vector_add=False,
         dry_run=False,
         save_config=False):
    check_hostname = not no_check_hostname
    obj_name = None if not obj_name else obj_name    
    env = datapower.Environment(appliances,
                                credentials,
                                timeout=timeout,
                                check_hostname=check_hostname)
    for appliance in env.appliances:
        print appliance.hostname
        if "all-domains" in domains:
            domains = appliance.domains        
        for domain in domains:
            print "\t", domain
            print obj_class, obj_name
            config = appliance.get_config(_class=obj_class,
                                          name=obj_name,
                                          domain=domain)
            objs = config.xml.findall(datapower.CONFIG_XPATH)
            for obj in objs:
                name = obj.get("name")
                print "\t\t{}".format(name)
                appliance.request.clear()
                request = appliance.request.request(domain=domain).modify_config()[obj_class](name=name)
                for mod in mods:
                    key, value = mod.split("=")
                    if vector_add:
                        for node in obj.findall(key):
                            request.append(node)
                    request[key](value)
                if dry_run:
                    print appliance.request
                    continue
                resp = appliance.send_request()
                if resp:
                    print "\t\t\tOK"
                else:
                    print "\t\t\tERROR, see log for details"
            if save_config and not dry_run:
                appliance.SaveConfig(domain=domain)


if __name__ == "__main__":
    cli = Cli(main=main, description=__doc__)
    try:
        cli.run()
    except SystemExit:
        pass
    except:
        make_logger("error").exception("An unhandled exception occurred")
        raise

