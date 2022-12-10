[Back to index](./index.html)
<h1>MAST for IBM DataPower Version {0}</h1>
<h2>Installation Guide</h2>

[TOC]

# Introduction

The installation of MAST for IBM DataPower has been designed to be as easy as
possible. Let's first review the requirements:

# Requirements

* Linux
* Windows
* OS X (coming soon)
* That's it (Although we do suggest a machine with at least 4 CPUs and 8GB RAM,
but this is not a hard requirement)

## Security concerns

It is important to replace the key and cert in $MAST_HOME/etc/crypto with
trusted certificates and to update the key and cert configuration in
$MAST_HOME/etc/server.conf.

For those with serious concerns over security, it may be a good idea to configure
the appliance's management interface to listen only to the IP Address of the MAST
server. This is a good idea if you really need to restrict access to the DataPower,
but if your organization embraces a more distributed or agile management strategy
there is the option to install MAST on your team's workstation.

# Installing MAST

The server install is powered by [miniconda](http://conda.pydata.org/miniconda.html)

The easiest way to install MAST for IBM DataPower is to place the executable
in the directory you want your MAST installation and run it. If run this way,
it will create a subdirectory called mast and install there. There are other
options available for installation as well.

If you wish to install into a specific directory, you can simply pass a
`--prefix` option to the installer and provide the directory you would like mast to be
installed to it will be installed in this directory directly (ie it will not
create a mast subdirectory).

If you would like more details on the options provided by the installer please
execute the installer and pass in a `--help` flag.

# Installing mastd

The process of installing mastd as a service will vary depending on your target
operating system. Please follow the instructions for your particular platform.

## Windows

As part of a mast installation, a script is provided "mastd.bat". You can use this
script to install, control and remove the mastd service. You can install the mastd
service with the following command:

    :::batch
    mastd install
    mastd start

This will install mastd as a Windows service and it can be controlled and configured
as a standard Windows service. You can also provide certain parameters to control
how the service will run (ie which user to run as, or whether to start on boot),
please provide a "/?" option to mastd install to see all the available options.

## Linux

Because distributions vary greatly in how services are started (this is usually
called an init system and includes software such as SysVinit or systemd), we have
provided as much as we can to still be completely cross-platform. In the mast
installation directory, there is a script called mastd, which will start a
daemon. mastd accepts the following sub-commands: start, stop, restart and
status. When started it will create a "pid" file: "./var/run/mastd.pid" this
will contain the process id of the daemon.

Please consult your operating system's documentation on how to load this as a proper service.

# Conclusion

As you can see it is quite simple to install mast and get mastd installed as a service.
If you have any problems, questions or comments please email support@mcindi.com.
