@echo off

SET MAST_HOME=%~dp0

cd /d %MAST_HOME%

mast.bat -m mast.datapower.ssh %*
