@echo off
setlocal

SET MAST_HOME=<%MAST_HOME%>
SET MAST_VERSION=2.1.0

cd /d %MAST_HOME%
call set-env.bat

if "%~1"=="" (
  %MAST_HOME%\anaconda\Scripts\ipython
) else (
  %MAST_HOME%\anaconda\python %*
)
endlocal
