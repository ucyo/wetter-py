"""Configuration of the wetter application.

These functions handle the configuration of the application. It is responsible
for the following tasks:

- Implementation of a json parser for the WetterDB format
- Implementation of a toml parser for the configuration file
- Checking if configuration file matches the currently stored WetterDB
- Resolve indiscrepencies between configuration and WetterDB
"""


import datetime
import json
import os
from dataclasses import dataclass
from json import JSONEncoder

import pandas as pd
import platformdirs
import toml

from .conn import OpenMeteoArchiveMeasurements, QueryTicket, WetterDB, utcnow

APPNAME = "wetter"
APPAUTHOR = "ucyo"
DEFAULT_LAT = 49
DEFAULT_LON = 8.41

BASE_CONFIG = {"max_distance": 1, "location": {"lat": DEFAULT_LAT, "lon": DEFAULT_LON}}

BASE_STORE = {
    "lat": DEFAULT_LAT,
    "lon": DEFAULT_LON,
    "version": 1,
    "data": {
        "index": ["temperature", "wind"],
        "columns": ["2023-01-01T00:00:00.000000+0000", "2023-01-01T01:00:00.000000+0000"],
        "data": [[7.7, 12.7], [6.8, 13.0]],
    },
}

USER = os.environ.get("USER", os.environ.get("USERNAME"))

SYSTEMD_SERVICE = """[Unit]
Description=Update of wetter cli tool using systemd
Wants=wetter.timer

[Service]
Type=oneshot
ExecStart=/usr/bin/wetter update
User={0}

[Install]
WantedBy=multi-user.target
""".format(
    USER
)

SYSTEMD_TIMER = """[Unit]
Description=Update of wetter cli tool using systemd

[Timer]
OnCalendar=*-*-* *:05:05

[Install]
WantedBy=timers.target
"""


@dataclass
class Configuration:
    max_distance: int = 1
    config_path: str = os.path.join(platformdirs.user_config_dir(appname=APPNAME), f"{APPNAME}.toml")
    store_path: str = os.path.join(platformdirs.user_data_dir(appname=APPNAME, appauthor=APPAUTHOR), f"{APPNAME}.json")

    def __post_init__(self):
        self.load_config()
        self.max_distance = getattr(self.config, "max_distance", self.max_distance)
        self.load_store()
        self.check()

    def _print_systemd_service(self):
        if USER is None:
            raise Exception("Please define USER enviroment variable to correctly setup systemd")
        else:
            print(SYSTEMD_SERVICE)

    def _print_systemd_timer(self):
        print(SYSTEMD_TIMER)

    def check(self):
        assert "location" in self.config.keys()
        assert "lat" in self.config["location"].keys()
        assert "lon" in self.config["location"].keys()
        lat_diff = abs(self.config["location"]["lat"] - self.store.lat)
        lon_diff = abs(self.config["location"]["lon"] - self.store.lon)
        if lat_diff > self.max_distance or lon_diff > self.max_distance:
            self.location_changed(lat=self.config["location"]["lat"], lon=self.config["location"]["lon"])
        return True

    def location_changed(self, lat, lon):
        start = utcnow()
        end = start - datetime.timedelta(days=30)
        start = datetime.datetime(year=start.year - 1, month=1, day=1, tzinfo=start.tzinfo)
        qt = QueryTicket(lat=lat, lon=lon, start=start, end=end)
        api = OpenMeteoArchiveMeasurements
        # Request data from API
        print("Updating database from historical data API")
        resp = api.get(qt)
        if resp.status_code == 200:
            json = resp.json()
            df = api.parse(json)
            df = df[df.index <= qt.end]  # kick out predictions
        else:
            raise Exception(f"An error occurred during request [{resp.status_code}]: {resp.json()}")
        self.store.df = df
        self.store.lat = lat
        self.store.lon = lon
        print("Updating database from recent API")
        self.store.update()
        to_store(self.store)

    def load_config(self):
        path = self.config_path
        if not os.path.exists(path):
            self.generate_default_config()
        self.config = toml.load(path)

    def generate_default_config(self):
        path = self.config_path
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w") as f:
            toml.dump(BASE_CONFIG, f)

    def load_store(self):
        path = self.store_path
        if not os.path.exists(path):
            self.generate_default_store()
        with open(path, "r") as f:
            data = json.load(f, object_hook=DecodeDateTime)
        self.store = WetterDB(**data)
        self.check()

    def generate_default_store(self):
        path = self.store_path
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w") as f:
            json.dump(BASE_STORE, f, indent=4)

    def get_store(self):
        return self.store


def to_store(wetterdb):
    assert isinstance(wetterdb, WetterDB)
    dirname = platformdirs.user_data_dir(appname=APPNAME, appauthor=APPAUTHOR)
    path = os.path.join(dirname, f"{APPNAME}.json")
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


class WetterEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (datetime.date, datetime.datetime, pd.Timestamp)):
            return serialize_date(obj)


def DecodeDateTime(wetter_dict):
    if "columns" in wetter_dict:
        wetter_dict["columns"] = [deserialize_date(x) for x in wetter_dict["columns"]]
    return wetter_dict
