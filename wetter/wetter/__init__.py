"""Wetter - a command line tool to gather current weather information.

The goal of the application is to provide an easy command line (CLI) tool
for getting information about the current weather situation in your favourite city.
It currently has following features:

- Current/latest measurements
- Measurements from the last week, last month and last year
- Measurements for a specific month (either of this year if the month already
  passed or of last year)

The library is split into two core submodules, one application module and one tools(et) module.
Each of these submodules are responsible for different aspects of the systems.

The [config](./config) module is responsible for the configuration of the application,
for sane default definitions and the (de)serialisation of the data.
It checks configuration files and if necessary creates them. It also
checks for changes in the configurations and if necessary redownloads the data
from the weather API services of external resources.

The second big submodule is [backend](./backend).
It handles the connection to external services to download the data,
the connection to the local storage and the queries executed on it.

The [tools.py](./tools.py) module includes helper tools for different aspects
of the package e.g. logging. Finally, the [app.py](./app.py)
module handles the interface to the user.
It is responsible for parsing the user input and calling the backend.
It additionally handles the formating of the results for a nice view by the user.
"""
from . import backend
from .tools import logio, setup_logging


def get_version():
    """Return current version of library.

    This uses the version provided/setup in poetry.

    :return: Version number of library
    :rtype: str
    """
    try:
        # try new metadata package
        from importlib import metadata

        return metadata.version("wetter")
    except ImportError:
        # backup routine if Python version <= 3.7
        import pkg_resources

        return pkg_resources.get_distribution("wetter").version


__version__ = get_version()
