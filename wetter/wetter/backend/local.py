"""This modules defines the necessary structure to save and access the local data.

It defines the `WetterDB` data structure which makes the local data accessible.
It defines the process to (de)serialize the data store to json, executes
check on the internal pd.DataFrame object if it is consistent and coherent with
assumptions made beforehand and defines the workflow for an update.
"""
import logging
from datetime import datetime as dt

import pandas as pd

from wetter.backend.extern import APIForWeatherData, OpenMeteoMeasurements, QueryTicket
from wetter.tools import utcnow

# from wetter import logio

log = logging.getLogger(__name__)


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

    # @logio(log)
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

    # @logio(log)
    def update(self, start=None, end=None, lat=None, lon=None, api=OpenMeteoMeasurements):
        """Update of a database at a given location.

        :param api: API to be used for measurement updates
        :type api: APIForWeatherData
        :param until: Date until which the update should be done [default: now()]
        :type until: Datetime
        :return: Latest and updated weather measurements
        :rtype: pd.DataFrame
        :raises: Exception (if response status code != 200), AssertionError
        """
        if end is None:
            end = utcnow()
        if start is None:
            start = self.df.index.max()
        if lat is None:
            lat = self.lat
        if lon is None:
            lon = self.lon
        assert isinstance(end, dt), "End date must be a datetime object"
        assert isinstance(start, dt), "Start date must be a datetime object"
        assert end.tzinfo is not None, "End date must have a timezone"
        assert start.tzinfo is not None, "Start date must have a timezone"
        assert issubclass(api, APIForWeatherData), "API must be an APIForWeatherData"

        # Build parameters for query
        qt = QueryTicket(start=start, end=end, lat=lat, lon=lon)

        # Request data from API
        resp = api.get(qt)
        if resp.status_code == 200:
            json = resp.json()
            df = api.parse(json)
            df = df[df.index <= qt.end]  # kick out predictions

            # Merge old and new data as well as eliminate duplicates and prediction data
            # (Some API provide forecast data which are not of interest for us)
            df = pd.concat([self.df, df])
            df = df[~df.index.duplicated(keep="last")]
            self.df = df
            self.lat = lat
            self.lon = lon
        else:
            log.error(f"An error occurred during request [{resp.status_code}]: {resp.json()}", exc_info=True)
            print(f"A connection error occured with the API provider: {resp.status_code} {resp.json()}.")
            print("Please try again at a later time or change your input.")
