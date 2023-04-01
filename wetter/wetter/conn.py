import json
import os
from dataclasses import dataclass
from datetime import datetime as dt
from datetime import timezone as tz

import numpy as np
import pandas as pd
import requests as rqs
from pytz import UTC

DATA_LOCATION = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data")
DB = os.path.join(DATA_LOCATION, "data.json")


def get_db():
    return WetterDB(DB)


class WetterDB:
    def __init__(self, filename):
        with open(filename, "r") as f:
            self._raw_data = json.load(f)
        number_of_measurements = len(self._raw_data["data"])
        measurements = {self._raw_data["index"][i]: self._raw_data["data"][i] for i in range(0, number_of_measurements)}
        df = pd.DataFrame({"time": self._raw_data["columns"], **measurements})
        df = df.set_index("time")
        df.index = df.index.astype(np.datetime64).tz_localize("UTC")
        self.df = df
        self.check_df()

    def check_df(self):
        assert "temperature" in self.df.columns
        assert "wind" in self.df.columns
        assert self.df.ndim == 2
        assert self.df.shape[1] == 2
        assert self.df.index.size > 0
        assert self.df.index[0].tzinfo == UTC

    def __getattr__(self, name):
        try:
            return self.__dict__[name]
        except KeyError:
            return getattr(self.df, name)

    @staticmethod
    def update(db_location, dry_run=False):
        base = WetterDB(db_location)
        latest = base.df.index.max()
        now = dt.utcnow().astimezone(tz.utc)
        qt = QueryTicket(start=latest, end=now)
        new_measurements = OpenMeteoMeasurements.get(qt)
        df = pd.concat([base.df, new_measurements])
        df = df[~df.index.duplicated(keep="last")]
        if not dry_run:
            df.T.to_json(db_location, orient="split", date_format="iso")
        return df


class OpenMeteoMeasurements:
    @staticmethod
    def parse(response):
        df = pd.DataFrame(
            {
                "time": [dt.strptime(x, "%Y-%m-%dT%H:%M").astimezone(tz=tz.utc) for x in response["hourly"]["time"]],
                "temperature": response["hourly"]["temperature_2m"],
                "wind": response["hourly"]["windspeed_10m"],
            }
        )
        df = df.set_index("time")
        return df

    @staticmethod
    def url():
        return (
            "https://api.open-meteo.com/v1/forecast?"
            + "latitude={lat:.2f}&longitude={lon:.2f}&"
            + "timezone={tz}&start_date={start}&end_date={end}&"
            + "hourly=temperature_2m,windspeed_10m,weathercode&current_weather=true"
        )

    @staticmethod
    def archive():
        return (
            "https://archive-api.open-meteo.com/v1/archive?"
            + "latitude={lat:.2f}&longitude={lon:.2f}&"
            + "timezone={tz}&start_date={start}&end_date={end}&"
            + "hourly=temperature_2m,windspeed_10m"
        )

    @staticmethod
    def get(qt):
        assert isinstance(qt, QueryTicket)
        url = OpenMeteoMeasurements.url()
        api = url.format(
            lat=qt.lat,
            lon=qt.lon,
            tz=qt.tz,
            start=qt.start.strftime("%Y-%m-%d"),
            end=qt.end.strftime("%Y-%m-%d"),
        )
        resp = rqs.get(api)
        if resp.status_code == 200:
            json = resp.json()
            df = OpenMeteoMeasurements.parse(json)
            df = df[df.index <= qt.end]  # kick out predictions
        else:
            raise Exception(f"An error occurred during request [{resp.status_code}]: {resp.json()}")
        return df


@dataclass
class QueryTicket:
    start: dt.date
    end: dt.date
    lat: float = 49
    lon: float = 8.41
    tz: str = "UTC"

    def __post_init__(self):
        if self.start > self.end:
            tmp = self.start
            self.start = self.end
            self.end = tmp
