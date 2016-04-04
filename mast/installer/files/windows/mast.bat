@echo off

SET MAST_HOME=<%MAST_HOME%>
SET MAST_VERSION=2.1.0

cd /d %MAST_HOME%

if "%~1"=="" (
  %MAST_HOME%\anaconda\Scripts\ipython
) else (
  %MAST_HOME%\anaconda\python %*
)
