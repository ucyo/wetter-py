import toml
import json
from json import JSONEncoder
import platformdirs
import pandas as pd
from datetime import datetime as dt
import os

APPNAME = "wetter"
APPAUTHOR = "ucyo"
DEFAULT_LAT = 49
DEFAULT_LON = 8.41

BASE_CONFIG = {
    "location": {
        "lat": DEFAULT_LAT,
        "lon": DEFAULT_LON
    }
}

BASE_STORE = {
    'lat': DEFAULT_LAT,
    'lon': DEFAULT_LON,
    'version': 1,
    'data': {
        'index': [
            'temperature',
            'wind'
        ],
        'columns': [
            '2022-01-01T00:00:00.000000+0000',
            '2022-01-01T01:00:00.000000+0000'
        ],
        'data': [
            [
                9.2,
                9.5
            ],
            [
                3.8,
                4.3
            ]
        ]
    }
}

def load_config():
    dirname = platformdirs.user_config_dir(appname=APPNAME)
    path = os.path.join(dirname, f"{APPNAME}.toml")
    if not os.path.exists(path):
        generate_default_config(path)
    config = toml.load(path)
    return config

def generate_default_config(path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w') as f:
        parsed_toml = toml.load(BASE_CONFIG)
        toml.dump(parsed_toml, f)

def load_data():
    dirname = platformdirs.user_data_dir(appname=APPNAME, appauthor=APPAUTHOR)
    path = os.path.join(dirname, f"{APPNAME}.json")
    if not os.path.exists(path):
        generate_default_data(path)
    with open(path, "r") as f:
        data = json.load(f, object_hook=DecodeDateTime)
    return data

def generate_default_data(path):
    with open(path, 'w') as f:
        json.dump(BASE_STORE, f, indent=4)


def serialize_date(timestamp):
    form = "%Y-%m-%dT%H:%M:%S.%f%z"
    return timestamp.strftime(form)

def deserialize_date(encoded):
    form = "%Y-%m-%dT%H:%M:%S.%f%z"
    return dt.strptime(encoded, form)


class WetterEncoder(JSONEncoder):
        def default(self, obj):
            if isinstance(obj, (datetime.date, datetime.datetime, pd.Timestamp)):
                return serialize_date(obj)

def DecodeDateTime(wetter_dict):
   if 'time' in wetter_dict and isinstance(wetter_dict["time"], list):
    wetter_dict["time"] = [deserialize_date(x) for x in wetter_dict["time"]]
    return wetter_dict
