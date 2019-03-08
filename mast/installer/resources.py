
import platform

conda_dependencies = {
      "Windows": {
            "64bit": {
                  "pywin32": "https://anaconda.org/anaconda/pywin32/223/download/win-64/pywin32-223-py37hfa6e2cd_1.tar.bz2",
                  "vc": "https://anaconda.org/anaconda/vc/14.1/download/win-64/vc-14.1-h0510ff6_4.tar.bz2",
                  "pycrypto": "https://anaconda.org/anaconda/pycrypto/2.6.1/download/win-64/pycrypto-2.6.1-py37hfa6e2cd_9.tar.bz2",
                  "lxml": "https://anaconda.org/anaconda/lxml/4.3.1/download/win-64/lxml-4.3.1-py37h1350720_0.tar.bz2",
            },
            "32bit": {
                  "pywin32": "https://anaconda.org/anaconda/pywin32/223/download/win-32/pywin32-223-py37hfa6e2cd_1.tar.bz2",
                  "vc": "https://anaconda.org/anaconda/vc/14.1/download/win-32/vc-14.1-h0510ff6_4.tar.bz2",
                  "pycrypto": "https://anaconda.org/anaconda/pycrypto/2.6.1/download/win-32/pycrypto-2.6.1-py37hfa6e2cd_9.tar.bz2",
                  "lxml": "https://anaconda.org/anaconda/lxml/4.3.1/download/win-32/lxml-4.3.1-py37h1350720_0.tar.bz2",
            },
      },
      "Linux": {
            "64bit": {
                  "pycrypto": "https://anaconda.org/anaconda/pycrypto/2.6.1/download/linux-64/pycrypto-2.6.1-py37h14c3975_9.tar.bz2",
                  "lxml": "https://anaconda.org/anaconda/lxml/4.3.1/download/linux-64/lxml-4.3.1-py37hefd8a0e_0.tar.bz2",
            },
            "32bit": {
                  "pycrypto": "https://anaconda.org/anaconda/pycrypto/2.6.1/download/linux-32/pycrypto-2.6.1-py37h14c3975_9.tar.bz2",
                  "lxml": "https://anaconda.org/anaconda/lxml/4.2.5/download/linux-32/lxml-4.2.5-py27hefd8a0e_0.tar.bz2",
            },

      },
}
pip_dependencies = [
      "commandr",
      "cherrypy",
      "paramiko",
      "markdown",
      "ecdsa",
      "python-dateutil",
      "flask",
      "openpyxl",
      "pygments",
      "colorama",
      "git+https://github.com/mcindi/mast@python3#egg=mast",
]
if "Windows" in platform.system():
      pip_dependencies.insert(0, "pyreadline")
elif "Linux" in platform.system():
      pip_dependencies.insert(0, "sander-daemon")
