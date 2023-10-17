SET MAST_HOME=%~dp0
SET NOTEBOOK_HOME=%MAST_HOME%\notebooks

cd %NOTEBOOK_HOME%
%MAST_HOME%\anaconda\Scripts\ipython notebook %*
cd ..
