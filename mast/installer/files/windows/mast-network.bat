@echo off

SET MAST_HOME=<%MAST_HOME%>

cd %MAST_HOME%

mast -m mast.datapower.network %*

