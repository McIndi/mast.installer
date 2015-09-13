# mast.installer

## TODO

this is a list of todo items which I wish to include in the documentation,
so I am including them as if they are true, but listing them here so
readers are aware:

- [ ] move `build.py` to the root directory of the package
- [ ] write at least some tests
- [ ] have `build.py` create the installer in the root directory of the project
- [ ] implement installer options

## The Package

This package brings everything together in order to build an executable
installer. We have made every attempt to make this process as easy as
possible. Once you have the requirements installed it is very simple
to build the executable:

```
$ git clone --recursive https://github.com/mcindi/mast.installer
$ cd mast.installer
$ python build.py
```

this will create a native executable installer for the platform on which it
was run in the root directory of the project.

## The installer

The installer can be executed with no arguments, in which case it will install
MAST in the directory in which it resides. This form of installation requires
no internet connection. If you wish to install MAST into a different directory
you can provide a `-p` option and specify the desired directory. There are
some other options to specify how you would like to install MAST.

```
-p --prefix     - The directory in which to install MAST
-d --daemon     - Install mastd as a service
-n --net-install - pull the latest versions of everything instead of the bundled
                  versions.
-a --add-to-path       - add mast directory and anaconda's executables to the path of the
                  user executing the installer
```

## Requirements

1. Python 2.7
2. pyinstaller
3. py.test

## Links to the dependent packages

* [mast.xor](https://github.com/mcindi/mast.xor)
* [mast.timestamp](https://github.com/mcindi/mast.timestamp)
* [mast.pprint](https://github.com/mcindi/mast.pprint)
* [mast.plugin_utils](https://github.com/mcindi/mast.plugin_utils)
* [mast.plugins](https://github.com/mcindi/mast.plugins)
* [mast.logging](https://github.com/mcindi/mast.logging)
* [mast.hashes](https://github.com/mcindi/mast.hashes)
* [mast.datapower.web](https://github.com/mcindi/mast.datapower.web)
* [mast.datapower.system](https://github.com/mcindi/mast.datapower.system)
* [mast.datapower.status](https://github.com/mcindi/mast.datapower.status)
* [mast.datapower.ssh](https://github.com/mcindi/mast.datapower.ssh)
* [mast.datapower.network](https://github.com/mcindi/mast.datapower.network)
* [mast.datapower.developer](https://github.com/mcindi/mast.datapower.developer)
* [mast.datapower.deployment](https://github.com/mcindi/mast.datapower.deployment)
* [mast.datapower.datapower](https://github.com/mcindi/mast.datapower.datapower)
* [mast.datapower.backups](https://github.com/mcindi/mast.datapower.backups)
* [mast.datapower.accounts](https://github.com/mcindi/mast.datapower.accounts)
* [mast.daemon](https://github.com/mcindi/mast.daemon)
* [mast.cron](https://github.com/mcindi/mast.cron)
* [mast.config](https://github.com/mcindi/mast.config)
* [mast.cli](https://github.com/mcindi/mast.cli)
* [commandr](https://github.com/tellapart/commandr)
* [cherrypy](https://github.com/cherrypy/cherrypy)
* [paramiko](https://github.com/paramiko/paramiko)
* [markdown](https://github.com/waylan/Python-Markdown)
* [ecdsa](https://github.com/warner/python-ecdsa)
* [pycrypto](https://github.com/dlitz/pycrypto)
