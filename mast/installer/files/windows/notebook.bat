SET MAST_HOME=<%MAST_HOME%>
SET NOTEBOOK_HOME=<%MAST_HOME%>/notebooks

cd %NOTEBOOK_HOME%
../anaconda/ipython notebook %*

