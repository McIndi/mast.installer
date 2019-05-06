@echo off
setlocal

SET MAST_HOME=<%MAST_HOME%>

cd /d %MAST_HOME%
call set-env.bat

%MAST_HOME%\miniconda\python %*
endlocal
