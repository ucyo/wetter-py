"""Configuration module for storing the current settings in memory."""

import datetime
import json
import logging
import os
from dataclasses import dataclass

import platformdirs
import toml

from wetter import tools
from wetter.backend.extern import OpenMeteoArchiveMeasurements
from wetter.backend.local import WetterDB
from wetter.config.defaults import (
    APPAUTHOR,
    APPNAME,
    BASE_CONFIG,
    BASE_STORE,
    DEFAULT_CONFIG_PATH,
    SYSTEMD_SERVICE,
    SYSTEMD_TIMER,
    USER,
)
from wetter.config.parser import DecodeDateTime, to_store

log = logging.getLogger(__name__)


@dataclass
class Configuration:
    """Current configuration and storage files in one object.

    :param max_distance: Acceptable change in location coordinate changes until reload of data
    :type max_distance: int
    :param config_path: Location of configuration file
    :type config_path: str
    :param self_check: Flag if self check should be executed [default: True]
    :type self_check: bool
    :param store_path: Location of storage file
    :type store_path: str
    """

    max_distance: int = 1
    config_path: str = DEFAULT_CONFIG_PATH
    self_check: bool = True
    store_path: str = os.path.join(
        platformdirs.user_data_dir(appname=APPNAME, appauthor=APPAUTHOR),
        f"{APPNAME}.json",
    )

    def __post_init__(self):
        self._load_config()
        self.max_distance = getattr(self.config, "max_distance", self.max_distance)
        self._load_store()
        if self.self_check:
            self._check()

    def get_store(self):
        """Return the inner datastore

        :returns: WetterDB with all measurements
        :rtype: WetterDB
        """
        return self.store

    def _location_changed(self, lat, lon):
        start = tools.utcnow()
        end = start - datetime.timedelta(days=30)
        start = datetime.datetime(year=start.year - 1, month=1, day=1, tzinfo=start.tzinfo)
        print("Updating database from historical data API")
        self.store.update(start=start, end=end, lat=lat, lon=lon, api=OpenMeteoArchiveMeasurements)
        print("Updating database from recent API")
        self.store.update()
        to_store(self.store)

    def _load_config(self):
        path = self.config_path
        if not os.path.exists(path):
            self._generate_default_config()
        self.config = toml.load(path)

    def _load_store(self):
        path = self.store_path
        if not os.path.exists(path):
            self._generate_default_store()
        with open(path, "r") as f:
            data = json.load(f, object_hook=DecodeDateTime)
        self.store = WetterDB(**data)
        self._check()

    def _generate_default_config(self):
        path = self.config_path
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w") as f:
            toml.dump(BASE_CONFIG, f)

    def _generate_default_store(self):
        path = self.store_path
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w") as f:
            json.dump(BASE_STORE, f, indent=4)

    def _print_systemd_service(self):
        if USER is None:
            raise Exception("Please define USER enviroment variable to correctly setup systemd")
        else:
            print(SYSTEMD_SERVICE)

    def _print_systemd_timer(self):
        print(SYSTEMD_TIMER)

    def _check(self):
        assert "location" in self.config.keys()
        assert "lat" in self.config["location"].keys()
        assert "lon" in self.config["location"].keys()
        assert self.config["location"]["lon"] >= -180
        assert self.config["location"]["lon"] <= 180
        assert self.config["location"]["lat"] >= -90
        assert self.config["location"]["lat"] <= 90
        lat_diff = abs(self.config["location"]["lat"] - self.store.lat)
        lon_diff = abs(self.config["location"]["lon"] - self.store.lon)
        if lat_diff > self.max_distance or lon_diff > self.max_distance:
            self._location_changed(lat=self.config["location"]["lat"], lon=self.config["location"]["lon"])
        return True
