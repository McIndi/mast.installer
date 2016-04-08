@echo off

SET MAST_HOME=<%MAST_HOME%>

cd /d %MAST_HOME%

mast.bat -m mast.testsuite %*

