#!/usr/bin/env sh

export MAST_HOME=<%MAST_HOME%>

cd $MAST_HOME

./mast -m mast.datapower.ssh $@

