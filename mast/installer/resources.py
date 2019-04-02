
import platform

conda_dependencies = {
      "Windows": {
            "64bit": {
                  "vc": "https://anaconda.org/anaconda/vc/14.1/download/win-64/vc-14.1-h0510ff6_4.tar.bz2",
                  "pycrypto": "https://anaconda.org/anaconda/pycrypto/2.6.1/download/win-64/pycrypto-2.6.1-py27h0c8e037_9.tar.bz2",
            },
            "32bit": {
                  "vc": "https://anaconda.org/anaconda/vc/14.1/download/win-32/vc-14.1-h0510ff6_4.tar.bz2",
                  "pycrypto": "https://anaconda.org/anaconda/pycrypto/2.6.1/download/win-32/pycrypto-2.6.1-py27_2.tar.bz2",
            },
      },
      "Linux": {
            "64bit": {
                  "pycrypto": "https://anaconda.org/anaconda/pycrypto/2.6.1/download/linux-64/pycrypto-2.6.1-py27h14c3975_9.tar.bz2",
            },
            "32bit": {
                  "pycrypto": "https://anaconda.org/anaconda/pycrypto/2.6.1/download/linux-32/pycrypto-2.6.1-py27_0.tar.bz2",
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
      "lxml",
      "pygments",
      "colorama",
      "git+https://github.com/mcindi/mast#egg=mast",

]
if "Windows" in platform.system():
      pip_dependencies.insert(0, "pyreadline")
elif "Linux" in platform.system():
      pip_dependencies.insert(0, "sander-daemon")
