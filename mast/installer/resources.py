
import platform

conda_dependencies = {
      "Windows": {
            "64bit": {
                  "vc": "https://anaconda.org/anaconda/vc/14.1/download/win-64/vc-14.1-h0510ff6_4.tar.bz2",
            },
            "32bit": {
                  "vc": "https://anaconda.org/anaconda/vc/14.1/download/win-32/vc-14.1-h0510ff6_4.tar.bz2",
            },
      },
      "Linux": {
            "64bit": {
            },
            "32bit": {
            },

      },
}
pip_dependencies = [
      "commandr==1.5.0",
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
