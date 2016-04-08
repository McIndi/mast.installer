@echo off

SET MAST_HOME=<%MAST_HOME%>

cd /d %MAST_HOME%
set-env.bat

if "%~1"=="" (
  %MAST_HOME%\anaconda\Scripts\ipython
) else (
  %MAST_HOME%\anaconda\python %*
)
