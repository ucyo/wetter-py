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

from wetter import conn, queries


@pytest.fixture
def db():
    db = conn.get_db()
    yield db


def test_latest_measurement(db):
    date = dt(year=2023, month=2, day=2, hour=15, minute=2, tzinfo=tz.utc)
    df = queries.latest_datapoint(db.df, date)
    assert df.index.size == 1
    assert df.index[0] == date.replace(minute=0)


def test_latest_measurement_context_outside(db):
    date = dt(year=1922, month=2, day=2, hour=15, minute=2, tzinfo=tz.utc)
    df = queries.latest_datapoint(db.df, date)
    assert df.index.size == 0
    assert df.size == 0


def test_latest_measurement_utc_cest(db):
    berlin = tz(timedelta(hours=2))
    date = dt(year=2023, month=2, day=2, hour=15, minute=2, tzinfo=berlin)
    df = queries.latest_datapoint(db.df, date)
    assert df.index.size == 1
    assert df.index[0] == date.replace(hour=13, minute=0, tzinfo=tz.utc)
