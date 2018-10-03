@echo off
setlocal

SET MAST_HOME=<%MAST_HOME%>
SET MAST_VERSION=2.2.1

cd /d %MAST_HOME%
call set-env.bat

%MAST_HOME%\miniconda\python %*
endlocal
