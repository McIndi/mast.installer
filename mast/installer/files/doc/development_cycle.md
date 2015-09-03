# Build Servers

## Linux

__NOTE__ The build servers are strictly for building the installers. For
Linux we need to go with a relatively old version of linux because of the
lack of forward compatibility of the glibc library (which pyinstaller does
not include, but rather links against). We chose Fedora 14 for this.

With Fedora 14 (minimal install) the following steps are needed to set
up a build environment (These steps are the same for both 32 and 64 bit):

__as root__
```bash
$ service network start
$ yum install wget
$ yum install git
$ yum install python-pip
$ pip install pyinstaller
$ useradd mast_build
$ passwd mast_build
```

__as mast\_build__
```
$ cd /tmp
$ git clone --recursive https://github.com/mcindi/mast.installer
$ cd mast.installer/mast/installer/
$ ./linux_build.sh
```

## Windows

We are building on a Windows 10 Pro machine.

The following dependencies need to be installed:

1. git for windows
2. Anaconda Python Distribution (I use Anaconda because it makes everything
easier, but you can install the standard CPython, pywin32, pip and
pyinstaller to get everything you need)


To build on Windows:

```
C:\dir\> git clone --recursive https://github.com/mcindi/mast.installer
C:\dir\> cd mast.installer\mast\installer
C:\dir\mast.installer\mast\installer> python windows_build.py
```

# Continuous Delivery

We are using Jenkins to power our continuous delivery and continuous
integration. We offer 3 builds at the moment:

1. windows 64
2. Linux 32
3. Linux 64

We have others on the roadmap (pretty soon):

1. windows 64
2. Linux 32
3. Linux 64
4. windows 64 Minimal
5. Linux 32 Minimal
6. Linux 64 Minimal

and more in the slightly longer-term:

1. windows 64
2. Linux 32
3. Linux 64
4. OSx 64
5. windows 64 Minimal
6. Linux 32 Minimal
7. Linux 64 Minimal
8. OSx 64 Minimal

