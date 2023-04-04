"""Test file for the queries on the backend system.

This module will test the queries being executed for the cli tool.
Additionally it needs to be tested if the arguments and return values
for the functions are the same. Details about the queries can be found
in the appropiate documentation of the [wetter library](../wetter/queries.py).
"""
from datetime import datetime as dt
from datetime import timedelta
from datetime import timezone as tz

import pytest

from wetter import config, queries


@pytest.fixture
def db():
    db = config.Configuration().get_store()
    yield db


def test_latest_measurement(db):
    pass


def test_latest_measurement_context_outside(db):
    date = dt(year=1922, month=2, day=2, hour=15, minute=2, tzinfo=tz.utc)
    df = queries.latest_datapoint(db.df, date)
    assert df.index.size == 0
    assert df.size == 0


def test_latest_measurement_utc_cest():
    berlin = tz(timedelta(hours=2))
    date = dt(year=2023, month=1, day=1, hour=0, minute=0, tzinfo=berlin)
    utc_date = date.astimezone(tz.utc)
    assert utc_date.year == date.year - 1


@pytest.mark.long
def test_queries_considering_timezones(db):
    before = db.df[(db.df.index.month == 1) & (db.df.index.year == 2022)].mean()
    db.df.index = db.df.index.map(lambda x: x.astimezone(7200))
    after = db.df[(db.df.index.month == 1) & (db.df.index.year == 2022)].mean()
    assert before["temperature"] != after["temperature"]
    assert before["wind"] != after["wind"]
