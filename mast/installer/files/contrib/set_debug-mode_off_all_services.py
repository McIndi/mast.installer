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
from mast.pprint import pprint_xml_str, pprint_xml
from lxml import etree
import os
import re

__version__ = "{}-0".format(os.environ["MAST_VERSION"])

def main(appliances=[],
         credentials=[],
         timeout=120,
         no_check_hostname=False,
         domains=[],
         ignore_unsaved=False,
         dry_run=False,
         save_config=False):
    check_hostname = not no_check_hostname
    env = datapower.Environment(
        appliances,
        credentials,
        timeout=timeout,
        check_hostname=check_hostname,
    )
    debug_mode_off = etree.fromstring("<DebugMode>off</DebugMode>")
    for appliance in env.appliances:
        print(appliance.hostname)
        _domains = domains
        if "all-domains" in domains:
            _domains = appliance.domains
        for domain in _domains:
            changed = False
            print("\t", domain)
            config = appliance.get_config(domain=domain, persisted=False)
            config = etree.fromstring(str(config))
            objs = config.xpath('.//*[./DebugMode/text()="on"]')
            if len(objs):
                change = True
            for obj in objs:
                if not ignore_unsaved and obj.find("DebugMode").attrib.get("persisted") == "false":
                    appliance.request.clear()
                    request = appliance.request.request(domain=domain).modify_config()[obj.tag](name=obj.attrib.get("name"))
                    request.append(debug_mode_off)
                    if not dry_run:
                        print((appliance.send_request()))
                    else:
                        print((appliance.request))
            if save_config and not dry_run and changed:
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
