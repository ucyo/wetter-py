"""Test file for the backend connection.

the functions in this file are being used to test the backend service
of the application. It is responsible for the following tasks:

- Testing the structure of the data being saved as json
- Testing the communication to weather APIs
- Testing the update process
"""
# import os
from datetime import datetime as dt
from datetime import timedelta as td
from datetime import timezone as tz

import pytest

from wetter.backend.extern import (
    APIForWeatherData,
    OpenMeteoArchiveMeasurements,
    OpenMeteoMeasurements,
    QueryTicket,
)
from wetter.config.config import Configuration


@pytest.fixture
def db():
    db = Configuration(store_path="./tests/testdata.json", self_check=False).get_store()
    yield db


def test_correct_naming(db):
    assert "temperature" in db.columns
    assert "wind" in db.columns
    assert isinstance(db.index[0], dt)


def test_db_has_no_empty_values(db):
    assert db.isna()._values.sum() == 0


@pytest.mark.web
def test_too_old():
    start = dt(year=1201, month=1, day=1)
    end = dt.now()
    qt = QueryTicket(start=start, end=end, lat=49, lon=8.41)
    assert OpenMeteoMeasurements.get(qt).status_code != 200


@pytest.mark.web
def test_open_meteo_archive_access():
    start = dt(year=2022, month=1, day=1)
    end = dt.now().replace(year=2022)
    qt = QueryTicket(start=start, end=end, lat=49, lon=8.41)
    assert OpenMeteoArchiveMeasurements.get(qt).status_code == 200


wrong_input = [dt(year=2022, month=1, day=1), 3, dt(year=1672, month=1, day=2, tzinfo=tz(td(0)))]


@pytest.mark.web
@pytest.mark.parametrize("end", wrong_input)
def test_wrong_end_date_for_update(end, db):
    with pytest.raises(Exception):
        db.update(until=end)


good_input = [
    (dt(year=2023, month=1, day=2, tzinfo=tz(td(0))), OpenMeteoArchiveMeasurements),
    (None, OpenMeteoMeasurements),
]


@pytest.mark.web
@pytest.mark.parametrize("end,api", good_input)
def test_correct_end_date_for_update(end, api, db):
    before = db.size
    db.update(until=end, api=api)
    assert before < db.size


def test_query_ticket_reversed_dates():
    end = dt.now()
    start = dt.now()
    qt = QueryTicket(start=start, end=end, lat=49, lon=8.41)
    assert qt.end == start
    assert qt.start == end


def test_serialization(db):
    db.df = db.df[:2]
    serialized = db.serialize()
    print(serialized)
    assert serialized["lon"] == 8.41
    assert serialized["lat"] == 49
    assert serialized["version"] == 1
    assert serialized["data"]["index"] == ["temperature", "wind"]


informal_api_call = ["parse", "get", "url"]


@pytest.mark.parametrize("method", informal_api_call)
def test_initialization_of_informal_api(method, db):
    qt = QueryTicket(db.df.index[0], db.df.index[1], db.lat, db.lon)
    correct_input = {} if method == "parse" else qt
    api = APIForWeatherData
    with pytest.raises(AssertionError):
        getattr(api, method)(1)
    with pytest.raises(NotImplementedError):
        getattr(api, method)(correct_input)
