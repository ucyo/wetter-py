"""Wetter - a command line tool to gather current weather information.

The goal of the application is to provide an easy command line (CLI) tool
for getting information about the current weather situation in Karlsruhe.
It allows for querying for the following data:

- Current/latest measurements
- Measurements from the last week, last month and last year
- Measurements for a specific month (either of this year if the month already
  passed or of last year)

The library is split to three separate submodules.
Each of these submodules are responsible for different aspects of the systems.
The [conn.py](./conn.py) is responsible for the backend.
It handles the connection to the database and unifies the input and output.
The [queries.py](./queries.py) is responsible for querying the
database returned by [conn.py](./conn.py).
It handles the proper selection of the data according to the requested time range.
Finally, the [cli.py](./cli.py) module handles the interface to the user.
It is responsible for parsing the user input and calling the backend.
It additionally handles the formating of the results for a nice view by the user.
"""


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
