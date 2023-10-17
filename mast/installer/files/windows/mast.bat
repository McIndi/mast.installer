@echo off
setlocal

SET MAST_HOME=%~dp0

cd /d %MAST_HOME%
call set-env.bat

%MAST_HOME%\python\%PYTHON_VERSION%\python %*
endlocal
