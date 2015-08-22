@echo off

SET MAST_HOME=<%MAST_HOME%>
SET PATH=<%MAST_HOME%>\anaconda;<%MAST_HOME%>\anaconda\Scripts;%PATH%

%MAST_HOME%\anaconda\python %*
