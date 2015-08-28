# Build Servers

__NOTE__ The build servers are strictly for building the installers. For
Linux we need to go with a relatively old version of linux because of the
lack of forward compatibility of the glibc library (which pyinstaller does
not include, but rather links against). We chose Fedora 14 for this.

With Fedora 14 (minimal install) the following steps are needed to set
up a build environment (These steps are the same for both 32 and 64 bit):

```bash
$ service network start
$ yum install wget
$ yum install git
$ yum install python-pip
$ pip install pyinstaller
$ useradd mast_build
$ passwd mast_build
$ su - mast_build
$ cd /tmp
$ git clone --recursive https://github.com/mcindi/mast.installer
$ cd mast.installer/mast/installer/
$ cd ../..
$ mv install.spec.linux install.spec
$ pyinstaller --onefile install.spec
```

