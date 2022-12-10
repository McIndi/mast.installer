[Back to index](./index.html)
<h1>MAST for IBM DataPower Version {0}</h1>
<h2>Release Notes</h2>

[TOC]

# MAST Version 3.0.4

## Bug Fixes

* Python 3 compatibility changes

# MAST Version 3.0.3

## Bug Fixes

* Python 3 compatibility changes

# MAST Version 3.0.2

## Bug Fixes

* Python 3 compatibility changes

# MAST Version 3.0.1

## Bug Fixes

* Python 3 compatibility changes

# MAST Version 3.0.0

## Bug Fixes

* Python 3 compatibility changes

# MAST Version 2.4.4

## Enhancements

* Add dprm.py to contrib scripts to allow removal of wildcarded files and directories from a group of appliances
* Add all-config.py to contrib scripts which presents a very robust view of the services running on your appliances

## Features

* The xor key is now configurable in xor.conf
* Significant features added for extract-service
* compare_files.py will now output filename and hash sorted properly
* Updated to latest version of JQuery

## Bug Fixes

* Fixed a bug which caused AccessPolicies to not be url encoded when adding a UserGroup from the Web GUI
* Fixed a bug caused by a typo in statmon.py
* MAST will now raise an error when attempting to add invalid node to a SOMA request instead of silently ignoring it


# MAST Version 2.4.3

We are pleased to present the MAST v 2.4.3 update which fixes a number of new features and provides a single bug fix. Please find a complete list of these new features and bug fixes below.

## Features

* Added xcfgdiff.py to compare a collection of xcfg files to contrib.
* Added the ability to specify a common deployment policy in service-config.conf which will be applied to every import (except environment specific configuration) during a git-deploy deployment.
* Added the ability to use environments defined in environments.conf as the hostname portion of a definition in service-config.conf.

## Bug Fixes

* Fixed a bug in contrib/statmon.py which caused a crash when a field was present in only a subset of readings.

# Mast Version 2.4.2

We are pleased to announce the 2.4.2 update to MAST for IBM DataPower. Please see below for the bug fixes and improvements.

## Enhancements

* Added compare-files.py to compare configuration and xsl files to contrib.
* Added sortxml.py to alphabetize xml elements (mostly for comparing xcfg files).

## Bug Fixes

* mast-developer export, when run in XML mode will now correctly use the .xcfg file extension.
* Fix issue when using a password with a colon ":"
* Fixed an issue on windows which caused crashes when using fs-sync.py with spaces in some filenames.
* Fixed an issue on windows when using git-deploy with the same --out-dir as a previous run since git was marking object files as read-only.

# MAST Version 2.4.1

McIndi Solutions, LLC is pleased to announce the 2.4.1 release of Mast for IBM DataPower. The changelog is below:

## Usability

* Removed delay from output of git-deploy in mast-web

## Features

* Added an option to suppress forced password change when creating a new user

## Bug fixes

* Improved handling of errors occurring during a git clone, pull and checkout in git-deploy
* Fixed logic in git-deploy to remove trailing slashes from repo urls
* Fixed a bug which caused failures when a colon was in a users password
* Fixed some dependency issues which caused non-impacting errors during installation and updates

# MAST Version 2.4.0

We are pleased to present the MAST v 2.4.0 update which fixes several bugs and provides a quite a few new features. Please find a complete list of these new features and bug fixes below.

As always feel free to email us at mastsupport@mcindi.com with any feature requests or bug reports.

## Features

* Add functionality to restart domain in mast-system
* Add functionality to add password map alias in mast-deployment
* Add functionality to delete password map alias in mast-deployment
* (Temporary solution) Added a script to output mast version
* Change default max log size to 2.5M to make it easier to email logs
* Add timestamp to logging directories
* git-deploy will now sort exports by filename
    * Common configuration will be sorted by filename
    * Environment specific configuration will be sorted by filename
    * This allows one to prefix export filenames (ie 01-export.xcfg) to ensure  that configuration is imported in a specific order
* Added script to set default log to all at error
* Added script to disable all probes
* In git-deploy added an indication that the deployment policy will be imported
* git-deploy will now validate that backups are valid before continuing
       Bug fixes

## Bug Fixes

* Fixed bug which caused some passwords and credentials to be written to the logs
* Fix issue where multiple logging directories are being created
* Fix mast versioning
* Fix logging within the installer/updater
* Fix non-impacting bug where git-deploy would try to create local:



# MAST Version 2.2.0

Listed here are the changes which will affect how users will interact with
MAST for IBM DataPower, everything listed here is also listed below in the
changes section.

* Everything we have been shipping in the usrbin directory
will now be in the contrib directory, you should adjust any commands you may
have set in a scheduler or text file to use the form mast contrib/$scriptName
as opposed to mast usrbin/$scriptName. This change frees up the usrbin directory
to be used for user specific scripts which will be left alone during upgrades.
* All scripts and options which contained underscores ("_") have been converted
to use dashes ("") instead in order to maintain consistency between commands.
* now mast-system reboot-appliance reboots the appliances serially avoiding
unplanned outages
* The `--no-check-hostname` parameter has been moved up in all commands to
ensure that it takes the `-n` short option. __BEWARE__ when performing a
secure backup, because this change affects the short option for
`--no-quiesce-before` and `--no-unquiesce-after`
* Documentation has been completly re-done to improve user experience,
there is still more to do, but we think what we have so far is a great
step forward

## Features

* We have added the abiliity to create a directory on multiple appliances
through the mast-system create-dir command (Which is also available through
the Web Gui in the system tab).
* We have added the ability to list enabled probes through the mast-developer
list-probes command (which is also available through the web gui in the
developer tab).
* A build-hotfix script was added to the contrib directory which will allow
users to apply the latest changes on their own instead of waiting for official
hotfixes. This will build a hotfix package and if a -i option is specified,
it will install it as well.
* A gendocs script was added to the contrib directory which will build a
fresh set of documentation in HTML format generated from the installed versions
of all MAST libraries.
* A cert-audit script was added to the contrib directory which will gather
subject, issuer, notBefore and notAfter from all CryptoCertificate objects
which are up and enabled. This outputs as an Excel spreadsheet.
* A cert-file-audit script was added to the contrib directory which
will gather appliance, domain, directory, filename, size, and date-modified
from all files in cert:, pubcert: and sharedcert:
* A track-autoconfig script was added to the contrib directory which
uses git to track the changes in your appliance's `.cfg` scripts over time
* A track-getconfig script was added to the contrib directory which
uses git to track the changes of the running and/or persisted configuration
of your appliances over time.
* A thorough-cert-audit script was added to the contrib directory which
pulls together tons of information from the filestore, CryptoExports, and
various object configurations and correlates all the information in an
Excel spreadsheet, This really deserves a look, but it can take a while
to run.
* MAST now includes the dulwich (under a dual Apache v2 and GPL v2 license)
Python package allowing us to natively interact with git repositories without
requiring an installation of git.

## Bug Fixes

* We have fixed inconsistencies between dashes and underscores in CLI commands.
* We have fixed an issue where dp-query needed both a StatusPprovider and an
ObjectClass to be provided, now you can specify one or both.
* A better error message is now provided by mast-developer export when an
ObjectClass or an object name is not specified.
* A better error message is now provided when no appliances are selected (by
having their checkbox checked at the top of the page) when attempting to
perform an action in the Web Gui.
* Leading and trailing whitespace is now removed from filenames in set-file
to avoid a bug in the DataPower firmware (A PMR is currently open about this
issue).
* We have fixed an issue with the installers -n option which caused
installation to fail.
* We have fixed an issue where the installers -n option would not install
the required data files resulting in a broken installation.
* pycrypto was removed from the installer since this package is included
with the installation of Anaconda and the builds usually failed because most
servers lack a proper build chain (which is the way it should be).
* The no-check-hostname option was removed from mast-system xor since it
never belonged there.
* Several bugs in the mast-deployment postdeploy command were fixed which
caused the module to be unusable.
* We have fixed an issue where under certain circumstances plaintext passwords
were visible in the logs when using mast-ssh.
* We have fixed an issue in mast-ssh where it would not know the appliance was
 finished with it's response causing the program to hang.
* We have fixed an issue in mast-ssh where it would fail to realize that
incorrect credentials were provided.
* We have fixed an issue with display-routing-table which prevented it from
falling back to RoutingStatus2 if RoutingStatus3 was unavailable from the
appliances firmware.
* We have fixed an issue where you were prevented from running mast commands
while mastd was running on Windows due to file locks on the log files.
* We have fixed an issue where mast-ssh would not log you into the
specified domain upon connection.

## Enhancements

* We have added a timeout parameter to mast-ssh which will close a
connection if a response to a command issued takes longer than the specified
timeout (defaults to 120 seconds).
* We have made it so fs-sync from-dp will now only retrieve the filestore
listing once. This provides a huge performance gain.
* We have added output to fs-sync from-dp when invoked through the CLI.
* We changed mast-system set-file to infer the filename from it's name on the
local filesystem if a target filename is not specified.
* We changed `mast-system reboot-appliance` to reboot the appliances serially
avoiding unplanned outages.
* The installer now has a way to install into the current directory without
creating a mast subdirectory
* Scripts we were shipping in usrbin are now in the contrib directory leaving
you free to modify usrbin without worrying about updates overriding the changes.
NOTE: By definition this fix will leave the current usrbin scripts alone, so
if you are not using them or if you have not made any changes to them you
should delete them and use the scripts in contrib
* The `--no-check-hostname` parameter has been moved up in all commands to
ensure that it takes the `-n` short option. __BEWARE__ when performing a
secure backup, because this change affects the short option for
`--no-quiesce-before` and `--no-unquiesce-after`

## Upstream

1. Anaconda 2.4.0 is now being used see their changelog here

# MAST Version 2.1.1

## Enhancements

* Improved versioning of MAST
* Enhanced statmon to support multiple --grep options and case-insensitive searches
* Updated chart.js to latest stable release
* Add option to ignore errors in fs-sync.py
* Added contributing guide to our documentation

## Features

* Added the basics of the user-facing automated testing suite
* Included a POC for modify-config script (This one still needs work, please submit issues to our issue tracker)

## Bug Fixes

* Changed mast.bat to set PATH during run, to avoid issues with shared
libraries not being found
* Fixed bug where latest build of pywin32 prevented mastd from starting/stoping/starting
* Fixed bug in linux version of set-env which prevented it from working
* Fixed a bug causing excess output when an error occurred in cert-audit
* Fixed a bug in formatting the output of gendocs
* Fixed rare bug causing import error during install and build-hotfix
