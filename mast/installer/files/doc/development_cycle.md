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
$ cd mast.installer/mast/installer/scripts/anaconda
$ wget https://3230d63b5fc54e62148e-c95ac804525aac4b6dba79b00b39d1d3.ssl.cf1.rackcdn.com/Anaconda-2.3.0-Linux-x86_64.sh
$ cd ../..
$ mv install.spec.linux install.spec
$ pyinstaller --onefile install.spec
```

