[Back to index](./index.html)
<h1>MAST for IBM DataPower Version {0}</h1>
<h2>Release Notes</h2>

[TOC]

# Introduction

MAST for IBM DataPower version {0} has quite a few improvements and
bugfixes. In this release we focused on stability and enduser experience
rather than new features, however, we do have a few new features which we
believe will help tremendously with maximizing your return on investment in
IBM DataPower. 

# Important Changes

Listed here are the changes which will affect how users will interact with
MAST for IBM DataPower, everything listed here is also listed below in the
changes section.

1. Everything we have been shipping in the usrbin directory
will now be in the contrib directory, you should adjust any commands you may
have set in a scheduler or text file to use the form mast contrib/$scriptName
as opposed to mast usrbin/$scriptName. This change frees up the usrbin directory
to be used for user specific scripts which will be left alone during upgrades.
2. All scripts and options which contained underscores ("_") have been converted
to use dashes ("") instead in order to maintain consistency between commands.
3. now mast-system reboot-appliance reboots the appliances serially avoiding
unplanned outages
4. The `--no-check-hostname` parameter has been moved up in all commands to
ensure that it takes the `-n` short option. __BEWARE__ when performing a
secure backup, because this change affects the short option for
`--no-quiesce-before` and `--no-unquiesce-after`
5. Documentation has been completly re-done to improve user experience,
there is still more to do, but we think what we have so far is a great
step forward

# Changes

## Features

1. We have added the abiliity to create a directory on multiple appliances
through the mast-system create-dir command (Which is also available through
the Web Gui in the system tab).
2. We have added the ability to list enabled probes through the mast-developer
list-probes command (which is also available through the web gui in the
developer tab).
3. A build-hotfix script was added to the contrib directory which will allow
users to apply the latest changes on their own instead of waiting for official
hotfixes. This will build a hotfix package and if a -i option is specified,
it will install it as well.
4. A gendocs script was added to the contrib directory which will build a
fresh set of documentation in HTML format generated from the installed versions
of all MAST libraries.
5. A cert-audit script was added to the contrib directory which will gather
subject, issuer, notBefore and notAfter from all CryptoCertificate objects
which are up and enabled. This outputs as an Excel spreadsheet.
6. A cert-file-audit script was added to the contrib directory which
will gather appliance, domain, directory, filename, size, and date-modified
from all files in cert:, pubcert: and sharedcert:
7. A track-autoconfig script was added to the contrib directory which
uses git to track the changes in your appliance's `.cfg` scripts over time
8. A track-getconfig script was added to the contrib directory which
uses git to track the changes of the running and/or persisted configuration
of your appliances over time.
9. A thorough-cert-audit script was added to the contrib directory which
pulls together tons of information from the filestore, CryptoExports, and
various object configurations and correlates all the information in an
Excel spreadsheet, This really deserves a look, but it can take a while
to run.
10. MAST now includes the dulwich (under a dual Apache v2 and GPL v2 license)
Python package allowing us to natively interact with git repositories without
requiring an installation of git.

## Bugs

1. We have fixed inconsistencies between dashes and underscores in CLI commands.
2. We have fixed an issue where dp-query needed both a StatusPprovider and an
ObjectClass to be provided, now you can specify one or both.
3. A better error message is now provided by mast-developer export when an
ObjectClass or an object name is not specified.
4. A better error message is now provided when no appliances are selected (by
having their checkbox checked at the top of the page) when attempting to
perform an action in the Web Gui.
5. Leading and trailing whitespace is now removed from filenames in set-file
to avoid a bug in the DataPower firmware (A PMR is currently open about this
issue).
6. We have fixed an issue with the installers -n option which caused
installation to fail.
7. We have fixed an issue where the installers -n option would not install
the required data files resulting in a broken installation.
8. pycrypto was removed from the installer since this package is included
with the installation of Anaconda and the builds usually failed because most
servers lack a proper build chain (which is the way it should be).
9. The no-check-hostname option was removed from mast-system xor since it
never belonged there.
10. Several bugs in the mast-deployment postdeploy command were fixed which
caused the module to be unusable.
11. We have fixed an issue where under certain circumstances plaintext passwords
were visible in the logs when using mast-ssh.
12. We have fixed an issue in mast-ssh where it would not know the appliance was
 finished with it's response causing the program to hang.
13. We have fixed an issue in mast-ssh where it would fail to realize that
incorrect credentials were provided.
14. We have fixed an issue with display-routing-table which prevented it from
falling back to RoutingStatus2 if RoutingStatus3 was unavailable from the
appliances firmware.
15. We have fixed an issue where you were prevented from running mast commands
while mastd was running on Windows due to file locks on the log files.
16. We have fixed an issue where mast-ssh would not log you into the
specified domain upon connection.

## Enhancements

1. We have added a timeout parameter to mast-ssh which will close a
connection if a response to a command issued takes longer than the specified
timeout (defaults to 120 seconds).
2. We have made it so fs-sync from-dp will now only retrieve the filestore
listing once. This provides a huge performance gain.
3. We have added output to fs-sync from-dp when invoked through the CLI.
4. We changed mast-system set-file to infer the filename from it's name on the
local filesystem if a target filename is not specified.
5. We changed `mast-system reboot-appliance` to reboot the appliances serially
avoiding unplanned outages.
6. The installer now has a way to install into the current directory without
creating a mast subdirectory
7. Scripts we were shipping in usrbin are now in the contrib directory leaving
you free to modify usrbin without worrying about updates overriding the changes.
NOTE: By definition this fix will leave the current usrbin scripts alone, so
if you are not using them or if you have not made any changes to them you
should delete them and use the scripts in contrib
8. The `--no-check-hostname` parameter has been moved up in all commands to
ensure that it takes the `-n` short option. __BEWARE__ when performing a
secure backup, because this change affects the short option for
`--no-quiesce-before` and `--no-unquiesce-after`

## Upstream

1. Anaconda 2.4.0 is now being used see their changelog here
