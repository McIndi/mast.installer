from pygments.formatters import TerminalFormatter
from dulwich.repo import NotGitRepository
from pygments.lexers import DiffLexer
from dulwich import porcelain as git
from mast.timestamp import Timestamp
from mast.datapower import datapower
from mast.logging import make_logger
from io import StringIO
from pygments import highlight
import mast.pprint as pprint
from mast.cli import Cli
import colorama
import urllib.request, urllib.error, urllib.parse
import os
import re

colorama.init()


default_base_dir = os.path.join(os.environ["MAST_HOME"], "tmp", "config")
default_comment = "Update {}".format(Timestamp().friendly)
def main(appliances=[],
         credentials=[],
         timeout=120,
         no_check_hostname=False,
         base_dir=default_base_dir,
         comment=default_comment,
         persisted=False,
         recursive=False,
         no_strip_timestamp=False,
         page=False):
    """
    track_getconfig.py

    Description:

    Store running or persisted domain configuration in a local git
    repository for auditing purposes.

    Usage:

        :::bash
        $ mast contrib/track_getconfig.py --appliances <HOSTNAMES> --credentials <USER:PASS> --base-dir tmp/config

    Parameters:

    * `-a, --appliances` - The hostname(s), ip addresse(s), environment name(s)
    or alias(es) of the appliances you would like to affect. For details
    on configuring environments please see the comments in
    `environments.conf` located in `$MAST_HOME/etc/default`. For details
    on configuring aliases please see the comments in `hosts.conf` located
    in `$MAST_HOME/etc/default`.
    * `-c, --credentials`: The credentials to use for authenticating to the
    appliances. Should be either one set to use for all appliances
    or one set for each appliance. Credentials should be in the form
    `username:password` and should be provided in a space-seperated list
    if multiple are provided. If you would prefer to not use plain-text
    passwords, you can use the output of
    `$ mast-system xor <username:password>`.
    * `-t, --timeout`: The timeout in seconds to wait for a response from
    an appliance for any single request. __NOTE__ Program execution may
    halt if a timeout is reached.
    * `-n, --no-check-hostname`: If specified SSL verification will be turned
    off when sending commands to the appliances.
    * `-b, --base-dir`: The base directory where to store the downloaded
    files. Files will actually be stored in a subdirectory of `base_dir`
    named after the hostname in the form of `base_dir/<hostname>`
    * `-p, --persisted`: If specified, the persisted configuration will
    be retrieved as opposed to the running configuration (which is the
    default)
    * `-r, --recursive`: If specified, the configuration will be retrieved
    recursively to the extent of the facilities provided by DataPower
    * `-N, --no-strip-timestamp`: If specified, the timestamp will not be
    stripped from the XML document, This is done because we are tracking
    this information with git and stripping this out allows us to alert
    on any changes in the repository as opposed to special-casing the
    difference in timestamp.
    * `-P, --page`: If specified, page the output when too long to display
    at once
    """
    base_dir = os.path.abspath(base_dir)
    if not os.path.exists(base_dir):
        os.makedirs(base_dir)
    try:
        repo = git.Repo(base_dir)
        repo.head()
    except NotGitRepository:
        print("Initializing git repository")
        git.init(base_dir)
        git.add(base_dir)
        git.commit(base_dir, message="Initial Commit")
    except KeyError:
        git.add(base_dir)
        git.commit(base_dir, message="Initial Commit")

    check_hostname = not no_check_hostname
    env = datapower.Environment(appliances,
                                credentials,
                                timeout=timeout,
                                check_hostname=check_hostname)

    for appliance in env.appliances:
        appliance_directory = os.path.join(base_dir, appliance.hostname)
        if not os.path.exists(appliance_directory):
            os.mkdir(appliance_directory)
        for domain in appliance.domains:
            config = appliance.get_config(domain=domain,
                                          recursive=recursive,
                                          persisted=persisted)

            config = config.pretty
            if no_strip_timestamp:
                pass
            else:
                config = re.sub(r"^.*?<dp:timestamp>.*?</dp:timestamp>.*?$",
                                r"",
                                config,
                                flags=re.MULTILINE)

            filename = os.path.join(appliance_directory,
                                    "{}.xml".format(domain))
            with open(filename, "wb") as fout:
                fout.write(config)

    git.add(base_dir)
    print((git.status(base_dir)))
    git.commit(base_dir, message=comment)

    tmp = StringIO()
    git.show(base_dir, outstream=tmp)
    tmp.seek(0)
    out = highlight(tmp.read(), DiffLexer(), TerminalFormatter())
    if page:
        pprint.page(out)
    else:
        print(out)

if __name__ == "__main__":
    cli = Cli(main=main, description=main.__doc__)
    try:
        cli.run()
    except SystemExit:
        pass
    except:
        make_logger("error").exception("An unhandled exception occurred!")
        raise
