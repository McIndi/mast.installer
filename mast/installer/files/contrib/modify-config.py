"""
modify-config.py

POC for dynamically updating one or more attributes on groups of
objects.

To start you must specify the following options:

* `-a, --appliances`: The IP/hostname/environment/alias of the
appliances you wish to affect. Multiple entries must be in the form
of `-a host-1 -a host2`
* `-c, --credentials`: The credentials to use to authenticate to
the DataPower(s). Either one for all or one each (must be in the same
order as the appliances listed). Multiple entries must be in the form
of `-c user:pass -c user:pass`
* `-t, --timeout`: The timeout (in seconds) to wait for a response from
an appliance.
* `-n, --no-check-hostname`: If specified, ssl/tls verification will
be disabled
* `-d, --domains`: A list of domains to affect. You can pass in
"all-domains" to affect all domains, or you can specify one or more
domains by passing multiple arguments in the form of
`-d domain-1 -d domain-2`
* `-o, --obj-class`: The class of objects to affect. Only one object
class is permitted.
* `-O, --obj-name-filter`: A regular expression to filter affected objects
by name. Only objects with names matching the regular expression will be
affected.
* `--obj-filter`: A regular expression to filter affected objects. Only
objects whose XML formatted configuration contains a string matching
the regular expression will be affected.
* `-D, --dry-run`: If specified, no requests will be sent to the
appliances, instead the request that would've been sent to the
appliances is printed to stdout
* `-s, --save-config`: If specified, the configuration will be
persisted for each domain affected.

__Now for the interesting part__

* `-m, --mods`: These are the modifications to make to each object.
They should be in the form of "key=value" (I found it's best to keep
the quotes and on linux sometimes you will need to use single-quotes
to avoid shell expansion).

If the attribute you wish to change is nested within the configuration
you will need to use a "slash" seperator to seperate
elements (similar to an xpath expression). For instance, if you wish
to affect the "Disable-SSLv2" option of a CryptoProfile, you will need
to have something like: `--mods "SSLOptions/Disable-SSLv2=on"`.

If you need to perform a "vector-add", you will need to include that
in the `--mods` argument. For instance, if you are adding a secondary
address to an EthernetInterface, you would have pass in something like:
`--mods "(vector-add)SecondaryAddress=1.2.3.4/24"`

If the vector-add is nested, you will need to add the "(vector-add)"
directive to the actual element being modified like this:
`--mods "parent/(vector-add)child=value"`
"""
from collections import defaultdict
from itertools import groupby
from mast.datapower import datapower
from mast.logging import make_logger
from mast.cli import Cli
from mast.pprint import pprint_xml_str
import os
import re

__version__ = "{}-0".format(os.environ["MAST_VERSION"])

def tree():
    return defaultdict(tree)


def main(appliances=[],
         credentials=[],
         timeout=120,
         no_check_hostname=False,
         domains=[],
         obj_class="",
         obj_name_filter="",
         obj_filter="",
         mods=[],
         dry_run=False,
         save_config=False):
    check_hostname = not no_check_hostname
    env = datapower.Environment(appliances,
                                credentials,
                                timeout=timeout,
                                check_hostname=check_hostname)
    if obj_name_filter:
        obj_name_filter = re.compile(obj_name_filter)
    else:
        obj_name_filter = re.compile(".*")

    if obj_filter:
        obj_filter = re.compile(obj_filter)
    else:
        obj_filter = re.compile(".*")

    for appliance in env.appliances:
        print appliance.hostname
        _domains = domains
        if "all-domains" in domains:
            _domains = appliance.domains
        for domain in _domains:
            print "\t", domain
            print "\t\t", obj_class
            config = appliance.get_config(_class=obj_class,
                                          domain=domain)
            objs = config.xml.findall(datapower.CONFIG_XPATH)
            objs = filter(
                lambda x: obj_name_filter.search(x.get("name")),
                objs
            )
            objs = filter(
                lambda x: obj_filter.search(str(x)),
                objs
            )
            for obj in objs:
                name = obj.get("name")
                print "\t\t\t{}".format(name)
                appliance.request.clear()
                request = appliance.request.request(domain=domain).modify_config()[obj_class](name=name)

                parsed_mods = tree()
                for mod in mods:
                    k, v = mod.split("=")
                    if "/" in k:
                        ks = k.split("/")
                        level = parsed_mods
                        for _k in ks:
                            last_level = level
                            level = level[_k]
                        last_level[_k] = v
                    else:
                        parsed_mods[k] = v

                def append_mods(request, mods):
                    for k, v in mods.items():
                        if k.startswith("(vector-add)"):
                            k = k.replace("(vector-add)", "")
                            for node in obj.findall(k):
                                request.append(node)
                        if isinstance(v, defaultdict):
                            append_mods(request[k], v)
                        else:
                            request[k](v)
                append_mods(request, parsed_mods)

                if dry_run:
                    pprint_xml_str(str(appliance.request))
                    continue
                else:
                    resp = appliance.send_request()
                if resp:
                    print "\t\t\t\tOK"
                else:
                    print "\t\t\t\tERROR, see log for details"
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
