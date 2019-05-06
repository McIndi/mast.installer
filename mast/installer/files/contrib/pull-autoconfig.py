from mast.datapower import datapower
import mast.cli as cli
import os

def main(appliances=[],
         credentials=[],
         timeout=120,
         no_check_hostname=False,
         base_dir="."):
    check_hostname = not no_check_hostname
    env = datapower.Environment(
        hostnames=appliances,
        credentials=credentials,
        timeout=timeout,
        check_hostname=check_hostname)
    for appliance in env.appliances:
        _dir = os.path.join(base_dir, appliance.hostname)
        if not os.path.exists(_dir):
            os.makedirs(_dir)
        for domain in appliance.domains:
            if domain == "default":
                remote_name = "config:///autoconfig.cfg"
                local_name = os.path.join(_dir, "autoconfig.cfg")
                with open(local_name, "w") as fout:
                    contents = appliance.getfile(domain=domain, filename=remote_name)
                    fout.write(contents)
            else:
                remote_name = "config:///{}.cfg".format(domain)
                local_name = os.path.join(_dir, "{}.cfg".format(domain))
                with open(local_name, "w") as fout:
                    contents = appliance.getfile(domain=domain, filename=remote_name)
                    fout.write(contents)


if __name__ == "__main__":
    interface = cli.Cli(main=main)
    interface.run()
