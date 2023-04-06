"""The extern module handles the communication with external services.

The library needs to communicate with Weather APIs for getting the measurement
data. For future proofing this ability is abstracted. This helps future
developments and enables the addition of other API providesrs in the future.
The module has two core structures: (1) Interface descriptiono for API Weather Data
and (2) an query ticket for unifying the exchange to these servers.
"""

# from wetter.tools import logio
import logging
from dataclasses import dataclass
from datetime import datetime as dt
from datetime import timezone as tz

import pandas as pd
import requests as rqs

log = logging.getLogger(__name__)


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
        :raises: AssertionError
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
    """Implementation of the APIForWeatherData Interface for the Open Meteo Archive."""

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
    # @logio(log)
    def get(qt):
        """Get the data from REST API and parse the result.

        For details check superclass `APIForWeatherData`.
        """
        assert isinstance(qt, QueryTicket)
        url = OpenMeteoArchiveMeasurements.url(qt)
        result = rqs.get(url)
        return result


class OpenMeteoMeasurements(APIForWeatherData):
    """Implementation of the APIForWeatherData Interface for the Open Meteo."""

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
    # @logio(log)
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
