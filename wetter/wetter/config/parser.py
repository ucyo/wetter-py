"""This module defines the parsing of the json backend.

The only custom aspect of this definition are the timestamps used by
the backend system. Somehow the default json library can not handle
timestamps properly. Restricting the input/output to only full
timestamps i.e. including timezones prevents misusage.
"""

import datetime
import json
import os

import pandas as pd
import platformdirs

from wetter.backend.local import WetterDB
from wetter.config.defaults import APPAUTHOR, APPNAME


def to_store(wetterdb):
    """Store the data in memory to disk.

    :param wetterdb: The local measurements to be saved on disk
    :type wetterdb: WetterDB
    :raises: AssertionError
    """
    assert isinstance(wetterdb, WetterDB), f"Expected WetterDB, got {type(wetterdb)}"
    dirname = platformdirs.user_data_dir(appname=APPNAME, appauthor=APPAUTHOR)
    path = os.path.join(dirname, f"{APPNAME}.json")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    data = wetterdb.serialize()
    with open(path, "w") as f:
        result = json.dump(data, f, cls=WetterEncoder)
    return result


def serialize_date(timestamp):
    """Serialize timestamp (w/ timezone) to str."""
    form = "%Y-%m-%dT%H:%M:%S.%f%z"
    return timestamp.strftime(form)


def deserialize_date(encoded):
    """Deserialize str back to timestamp (w/ timezone)"""
    form = "%Y-%m-%dT%H:%M:%S.%f%z"
    return datetime.datetime.strptime(encoded, form)


class WetterEncoder(json.JSONEncoder):
    """Custom JSON Encoder for WetterDB data."""

    def default(self, obj):
        if isinstance(obj, (datetime.date, datetime.datetime, pd.Timestamp)):
            return serialize_date(obj)


def DecodeDateTime(wetter_dict):
    """Custom JSON Decoder function for WetterDB data."""
    if "columns" in wetter_dict:
        wetter_dict["columns"] = [deserialize_date(x) for x in wetter_dict["columns"]]
    return wetter_dict
