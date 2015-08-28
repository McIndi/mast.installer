#!/bin/bash
# Note that this will build an executable installer for MAST for
# IBM DataPower. The resulting binary will be stored in the directory
# "`pwd`/dist/install"  and will work on either 32 or 64 bit Linux
# systems depending on which platform this script is run
#
# This script has the following dependencies:
# 
# 1. wget
# 2. pyinstaller

# Quit if being built as root
if (( EUID == 0 )); then
   echo "You are building as root, this is unsupported" 1>&2
   exit 100
fi

# Download the appropriate Anaconda installer based on bitness
# For simplicities sake (ie I only have to check here) we name the output
# file the same regardless.
if [ "$(uname -m | grep '64')" != "" ]; then
    wget https://3230d63b5fc54e62148e-c95ac804525aac4b6dba79b00b39d1d3.ssl.cf1.rackcdn.com/Anaconda-2.3.0-Linux-x86_64.sh -O scripts/anaconda/anaconda-2.3.0-linux-install.sh
else
    wget https://3230d63b5fc54e62148e-c95ac804525aac4b6dba79b00b39d1d3.ssl.cf1.rackcdn.com/Anaconda-2.3.0-Linux-x86.sh -O scripts/anaconda/anaconda-2.3.0-linux-install.sh
fi

# having anything after install.spec causes strange behavior from pyinstaller
mv install.spec.linux install.spec
pyinstaller --onefile install.spec
