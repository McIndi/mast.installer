# MAST for IBM DataPower version 2.0.0

Thank you for using MAST for IBM DataPower version 2.0.0 this guide will
help you get started using our product. Don't worry, our product is designed
to be easy to install, configure and use.

## Getting Started

To get started you will first need to install MAST, so we will walk you
through the process on Windows and Linux. This is a simple process, and
it does not require any special privileges.

### Choosing an Installation Binary

TODO: We need to decide on what types of installers we want to include. Some
ideas:

* minimal - Only the necessary pieces (MiniConda)
* full - All of the tools included in a full Anaconda installation
* win 32, 64
* Lin 32, 64

### Installation

The installation is the same regardless of the installer chosen, just
be sure to choose an installer which is compatible with the target platform.

To install MAST for IBM DataPower simply execute the installer in the
directory you would like to install MAST into. If you wish to install into
a different directory, simply pass in a "-p" option and provide the desired
path (either fully-qualified or relative). The following options available
for the installer:

__TODO__: Finalize these options (only -p is implemented)

```
-p, --prefix            The directory into which you would like MAST to
                        be installed
-n, --no-network        Do not attempt to connect to the internet to install
                        or update any packages
-d, --daemon            Attempt to install the mastd daemon/service (requires
                        admin privileges)
-D, --delete            Delete the installer after installation
-N, --no-add-scripts    Do not add batch/shell scripts to MAST_HOME
-s, --set-mast-home     Attempt to set MAST_HOME environment variable
                        for current user
-a, --all-users         Install for all users (requires admin privileges)
```

### Configuration

The configuration system for MAST is designed to be simple and robust. In
MAST_HOME there are two directories `etc/default/` and `etc/local/`. Upon 
installation the local directory is empty. To change any options, simply
copy the relevant file from `etc/default/` into `etc/local/` and customize
any options you want. To reset the options to default, simply delete the file
from `etc/local/`. To get more information about each option please review
the comments in each configuration file.

### Usage

#### mastd

TODO: Write this

#### mast-web

TODO: Write this

#### The CLI

TODO: Write this

#### The GUI

TODO: Write this

#### The API

TODO: Write this

### Advanced Usage

#### py.test

TODO: Write this

#### mast.cron

TODO: Write this

#### git

git is included in MAST version 2.0.0