"""Backend of the wetter library.

This module handles the measurement data.
It is reponsible for defining a unified interface to the local data.
The includes the json structure of the data to be saved on the local machine.
as well as the update of the data using open API services.
The module defines three components:

- `WetterDB`: Read/Write/Update of the database
- `APIForWeatherData`: Definition of an API for access different WetterAPI services
- `QueryTicket`: Common data structure to abstract and regulate query parameters

The `WetterDB` reads and write data to the json backend store.
This can handle all the day to day queries of the cli tool.
If an update is necessary, then the other two components come in play.

The update process itself is a two step process.
First, a `QueryTicket` is defined.
It defines the data to be gathered from outside services e.g. [OpenMeteo](https://open-meteo.com/).
Afterwards this ticket is given to an API service for weather data.
Currently there is the OpenMeteo WeatherAPI service implemented.
Additional service might be added later on.
All API services need to be subclasses of `APIForWeatherData`.
This allows for an easy interchange of APIs.
"""

import time
from dataclasses import dataclass
from datetime import datetime as dt
from datetime import timezone as tz

import pandas as pd
import pytz
import requests as rqs

# UTC offset of user timezone
UTC_OFFSET_USER_TZ = -time.altzone if time.daylight else -time.timezone


def utcnow():
    return dt.utcnow().replace(tzinfo=tz.utc)


def now():
    return dt.now().replace(tzinfo=pytz.FixedOffset(UTC_OFFSET_USER_TZ / 60))


class APIForWeatherData:
    """Informal interface to external APIs.

    The informal interface defines a blueprint for the functions to
    be implemented by future APIs. This helps an easy exchange of the
    used API service for the update of the database.

    ¡Caution! This is not a strict interface and will be not enforced.
    But if it looks like a duck, ... :)
    """

    @staticmethod
    def parse(response):
        """Parse and transform the response in a format accepted by WetterDB.

        :param response: Response of API query
        :type response: dict
        :return: Measurements to be added to the WetterDB
        :rtype: pd.DataFrame
        """
        assert type(response) == dict
        raise NotImplementedError("Parsing is not implemented.")

    @staticmethod
    def url(qt):
        """URL of the API to be called.

        The URL will be filled out by the data saved in the QueryTicket.

        :param qt: The request parameters for the API call
        :type qt: QueryTicket
        :return: URL of API an http request should be send to
        :rtype: str
        """
        assert isinstance(qt, QueryTicket), f"Expected Queryticket, got {type(qt)}"
        raise NotImplementedError("URL is not setup.")

    @staticmethod
    def get(qt):
        """Get the data from REST API and parse the result.

        :param qt: The request parameters for the API call
        :type qt: QueryTicket
        :return: HTTP Response of the external API
        :rtype: requests.Response
        """
        assert isinstance(qt, QueryTicket), f"Expected Queryticket, got {type(qt)}"
        raise NotImplementedError("HTTP Get request to API not implemented.")


class OpenMeteoArchiveMeasurements(APIForWeatherData):
    @staticmethod
    def parse(response):
        """Parse and transform the response in a format accepted by WetterDB.

        For details check superclass `APIForWeatherData`.
        """
        assert type(response) == dict
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
    def url(qt):
        """URL of the API to be called.

        For details check superclass `APIForWeatherData`.
        """
        assert isinstance(qt, QueryTicket), f"Expected Queryticket, got {type(qt)}"
        url = (
            "https://archive-api.open-meteo.com/v1/archive?"
            + "latitude={lat:.2f}&longitude={lon:.2f}&"
            + "timezone={tz}&start_date={start}&end_date={end}&"
            + "hourly=temperature_2m,windspeed_10m"
        )
        return url.format(
            lat=qt.lat,
            lon=qt.lon,
            tz=qt.tz,
            start=qt.start.strftime("%Y-%m-%d"),
            end=qt.end.strftime("%Y-%m-%d"),
        )

    @staticmethod
    def get(qt):
        """Get the data from REST API and parse the result.

        For details check superclass `APIForWeatherData`.
        """
        assert isinstance(qt, QueryTicket)
        url = OpenMeteoArchiveMeasurements.url(qt)
        result = rqs.get(url)
        return result


class OpenMeteoMeasurements(APIForWeatherData):
    @staticmethod
    def parse(response):
        """Parse and transform the response in a format accepted by WetterDB.

        For details check superclass `APIForWeatherData`.
        """
        assert type(response) == dict
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
    def url(qt):
        """URL of the API to be called.

        For details check superclass `APIForWeatherData`.
        """
        assert isinstance(qt, QueryTicket), f"Expected Queryticket, got {type(qt)}"
        url = (
            "https://api.open-meteo.com/v1/forecast?"
            + "latitude={lat:.2f}&longitude={lon:.2f}&"
            + "timezone={tz}&start_date={start}&end_date={end}&"
            + "hourly=temperature_2m,windspeed_10m,weathercode&current_weather=true"
        )
        return url.format(
            lat=qt.lat,
            lon=qt.lon,
            tz=qt.tz,
            start=qt.start.strftime("%Y-%m-%d"),
            end=qt.end.strftime("%Y-%m-%d"),
        )

    @staticmethod
    def get(qt):
        """Get the data from REST API and parse the result.

        For details check superclass `APIForWeatherData`.
        """
        assert isinstance(qt, QueryTicket)
        url = OpenMeteoMeasurements.url(qt)
        result = rqs.get(url)
        return result


@dataclass
class QueryTicket:
    """Define, check and possibly restrict request parameters for APIs.

    An instance of `QueryTicket` defines the start and end date, the location
    using lat and lon coordinate, as well as the timezone of the output.
    Some consistency checks e.g. start date <= end date are done at creation.

    :param start: Start date of the measurements to be queried
    :type start: datetime.date
    :param end: End date of the measurements to be queried
    :type end: datetime.date
    :param lat: Latitude position of the measurements to be queried
    :type lat: float
    :param lon: Longitude position of the measurements to be queried
    :type lon: float
    :param tz: Timezone of the measurements to be queried [default: UTC]
    :type tz: str
    """

    start: dt.date
    end: dt.date
    lat: float
    lon: float
    tz: str = "UTC"

    def __post_init__(self):
        assert self.lon >= -180
        assert self.lon <= 180
        assert self.lat >= -90
        assert self.lat <= 90
        if self.start > self.end:
            tmp = self.start
            self.start = self.end
            self.end = tmp



class WetterDB:
    """Database of weather measurements for a single location.

    :param version: Version of current definition of schema
    :type version: int
    :param lat: Latitude position of the measurements to be queried
    :type lat: float
    :param lon: Longitude position of the measurements to be queried
    :type lon: float
    :param data: Key/Value store of pd.DataFrame (read from json)
    :type dict:
    """

    def __init__(self, version, lat, lon, data):
        self.version = version
        self.lat = lat
        self.lon = lon
        self._raw_data = data

        # Setup the measurements (flexibel for future updates)
        number_of_measurements = len(self._raw_data["data"])
        measurements = {self._raw_data["index"][i]: self._raw_data["data"][i] for i in range(0, number_of_measurements)}

        # Setup dataframe
        df = pd.DataFrame({"time": self._raw_data["columns"], **measurements})
        df = df.set_index("time")

        self.df = df
        self.check_df()

    def serialize(self):
        """Serialization of the entire data structure."""
        result = dict(data=self.df.T.to_dict(orient="split"))
        result["lat"] = self.lat
        result["lon"] = self.lon
        result["version"] = self.version
        return result

    def check_df(self):
        """Check assumptions about the database and its structure/schema.

        :raises: AssertionError
        """
        assert "temperature" in self.df.columns
        assert "wind" in self.df.columns
        assert self.df.ndim == 2
        assert self.df.shape[1] == 2
        assert self.df.index.size > 0
        assert self.df.index[0].tzinfo is not None

    def __getattr__(self, name):
        """Get attribute from inner `pd.DataFrame` if not provided by base class.

        The core compoment of the database is the internal `pd.DataFrame`
        object. This method helps calling the attributes of this core component
        by using the attributes of the WetterDB. First, the attributes of the
        WetterDB are returned. Should this result in an error, then the request
        is delegated to the `pd.DataFrame`. Any error on this level is not catched.

        :param name: Requested attribute name
        :type name: str
        :return: Requested Attribute
        :type: Not clear and based on the request
        :raises: KeyError
        """
        try:
            return self.__dict__[name]
        except KeyError:
            return getattr(self.df, name)

    def update(self, api=OpenMeteoMeasurements):
        """Update of a database at a given location.

        :param api: API to be used for measurement updates
        :type api: APIForWeatherData
        :return: Latest and updated weather measurements
        :rtype: pd.DataFrame
        :raises: Exception (if response status code != 200)
        """
        assert issubclass(api, APIForWeatherData)
        # Build parameters for query
        latest = self.df.index.max()
        now = utcnow()
        qt = QueryTicket(start=latest, end=now, lat=self.lat, lon=self.lon)

        # Request data from API
        resp = api.get(qt)
        if resp.status_code == 200:
            json = resp.json()
            df = api.parse(json)
            df = df[df.index <= qt.end]  # kick out predictions
        else:
            raise Exception(f"An error occurred during request [{resp.status_code}]: {resp.json()}")

        # Merge old and new data as well as eliminate duplicates and prediction data
        # (Some API provide forecast data which are not of interest for us)
        df = pd.concat([self.df, df])
        df = df[~df.index.duplicated(keep="last")]
        self.df = df
