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

# Considerations

There are a few options to consider before you install MAST for IBM DataPower.
First, there are two main installation bundles:

* Server
* Workstation

We will review the differences between these two options below:

## Server Install

The server install is designed to be as minimal as possible to serve the MAST
for IBM DataPower Web GUI. Though it is important to understand that because the
Web GUI is dynamically generated from the same code-base as the CLI, so CLI will
also be available from the server hosting MAST.

For those with serious concerns over security, it may be a good idea to configure
the appliance's management interface to listen only to the IP Address of the MAST
server. This is a good idea if you really need to restrict access to the DataPower,
but if your organization embraces a more distributed or agile management strategy
there is the option to install MAST on your team's workstation.

The server install is powered by [miniconda](http://conda.pydata.org/miniconda.html)

## Workstation Install

The workstation install is powered by Anaconda, find out more [here](https://www.continuum.io/why-anaconda)

If you choose the workstation installation, you will have access to many more
tools, which will enable your team to work with your appliances in a much more
agile way. A small list of tools which would be available in a workstation
install is listed here:

* py.test - A simple no-boilerplate testing framework
* spyder - A Python IDE useful for extending MAST's functionality
* IPython - An enhanced Python terminal useful for exploring MAST's Python API
* IPython notebook - An interactive computational environment, in which you can combine code execution, rich text, mathematics, plots and rich media.
* Python libraries to interact with Excel
* pandas - A library for data manipulation and analysis
* bokeh - An interactive visualization library that targets modern web browsers for presentation
* And tons more, see [why anaconda](https://www.continuum.io/why-anaconda)

# Installing MAST

Either way you go, installation is easy. Pre-built binaries are available to
those with a Support Contract as well as this documentation, so if you are
reading this you have received an email with links to both this documentation
and the binary installers. Please select the binary for your target platform.
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

As part of a mast installation, a script is provided "mastd.sh". You can use this
script to install, control and remove the mastd service. You can install the mastd
service with the following command:

    :::batch
    C:\mast\> mastd install

This will install mastd as a Windows service and it can be controlled and configured
as a standard Windows service. You can also provide certain parameters to control
how the service will run (ie which user to run as, or whether to start on boot),
please provide a "--help" option to mastd install to see all the available options.

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
