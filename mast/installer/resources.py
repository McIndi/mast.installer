
import platform

conda_dependencies = {
      "Windows": {
            "64bit": {
                  "pywin32": "https://anaconda.org/anaconda/pywin32/223/download/win-64/pywin32-223-py27h0c8e037_1.tar.bz2",
                  "vc": "https://anaconda.org/anaconda/vc/14.1/download/win-64/vc-14.1-h0510ff6_4.tar.bz2",
                  "pycrypto": "https://anaconda.org/anaconda/pycrypto/2.6.1/download/win-64/pycrypto-2.6.1-py27h0c8e037_9.tar.bz2",
                  "lxml": "https://anaconda.org/anaconda/lxml/4.3.0/download/win-64/lxml-4.3.0-py27h31b8cb8_0.tar.bz2",
            },
            "32bit": {
                  "pywin32": "https://anaconda.org/anaconda/pywin32/223/download/win-32/pywin32-223-py27h0c8e037_1.tar.bz2",
                  "vc": "https://anaconda.org/anaconda/vc/14.1/download/win-32/vc-14.1-h0510ff6_4.tar.bz2",
                  "pycrypto": "https://anaconda.org/anaconda/pycrypto/2.6.1/download/win-32/pycrypto-2.6.1-py27_2.tar.bz2",
                  "lxml": "https://anaconda.org/anaconda/lxml/4.3.0/download/win-32/lxml-4.3.0-py27h31b8cb8_0.tar.bz2",
            },
      },
      "Linux": {
            "64bit": {
                  "pycrypto": "https://anaconda.org/anaconda/pycrypto/2.6.1/download/linux-64/pycrypto-2.6.1-py27h14c3975_9.tar.bz2",
                  "lxml": "https://anaconda.org/anaconda/lxml/4.3.0/download/linux-64/lxml-4.3.0-py27hefd8a0e_0.tar.bz2",
            },
            "32bit": {
                  "pycrypto": "https://anaconda.org/anaconda/pycrypto/2.6.1/download/linux-32/pycrypto-2.6.1-py27_0.tar.bz2",
                  "lxml": "https://anaconda.org/anaconda/lxml/4.2.5/download/linux-32/lxml-4.2.5-py27hefd8a0e_0.tar.bz2",
            },

      },
}
pip_dependencies = [
      "commandr",
      "cherrypy<18.0.0",
      "paramiko",
      "markdown",
      "ecdsa",
      "python-dateutil",
      "flask",
      "openpyxl",
      "pygments",
      "colorama",
      "git+https://github.com/mcindi/mast#egg=mast@python3",
]
if "Windows" in platform.system():
      pip_dependencies.insert(0, "pyreadline")
elif "Linux" in platform.system():
      pip_dependencies.insert(0, "sander-daemon")
