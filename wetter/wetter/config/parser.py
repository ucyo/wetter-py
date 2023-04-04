import datetime
import json
import os

import pandas as pd
import platformdirs

from wetter.backend.local import WetterDB
from wetter.config.defaults import APPAUTHOR, APPNAME


def to_store(wetterdb):
    assert isinstance(wetterdb, WetterDB)
    dirname = platformdirs.user_data_dir(appname=APPNAME, appauthor=APPAUTHOR)
    path = os.path.join(dirname, f"{APPNAME}.json")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    data = wetterdb.serialize()
    with open(path, "w") as f:
        result = json.dump(data, f, cls=WetterEncoder)
    return result


def serialize_date(timestamp):
    form = "%Y-%m-%dT%H:%M:%S.%f%z"
    return timestamp.strftime(form)


def deserialize_date(encoded):
    form = "%Y-%m-%dT%H:%M:%S.%f%z"
    return datetime.datetime.strptime(encoded, form)


class WetterEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (datetime.date, datetime.datetime, pd.Timestamp)):
            return serialize_date(obj)


def DecodeDateTime(wetter_dict):
    if "columns" in wetter_dict:
        wetter_dict["columns"] = [deserialize_date(x) for x in wetter_dict["columns"]]
    return wetter_dict
