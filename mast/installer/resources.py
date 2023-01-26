
import platform

conda_dependencies = {
      "Windows": {
            "64bit": {
                  "vc": "https://anaconda.org/anaconda/vc/14.2/download/win-64/vc-14.2-h21ff451_1.tar.bz2",
            },
            "32bit": {
                  "vc": "https://anaconda.org/anaconda/vc/14.2/download/win-32/vc-14.2-h21ff451_1.tar.bz2",
            },
      },
      "Linux": {
            "64bit": {
            },
            "32bit": {
            },

      },
      "Darwin": {
            "64bit": {
            },
            "32bit": {
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
      "lxml",
      "pygments",
      "colorama",
      "git+https://github.com/mcindi/mast@python-3#egg=mast",

]
if "Windows" in platform.system():
      pip_dependencies.insert(0, "pyreadline")
      pip_dependencies.insert(0, "pywin32")
