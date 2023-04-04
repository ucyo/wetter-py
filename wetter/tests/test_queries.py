"""Test file for the queries on the backend system.

This module will test the queries being executed for the cli tool.
Additionally it needs to be tested if the arguments and return values
for the functions are the same. Details about the queries can be found
in the appropiate documentation of the [wetter library](../wetter/queries.py).
"""
from datetime import datetime as dt
from datetime import timedelta as td
from datetime import timezone as tz

import pytest

from wetter import tools
from wetter.backend import queries
from wetter.config import config


@pytest.fixture
def db():
    db = config.Configuration(store_path="./tests/testdata.json", self_check=False).get_store()
    yield db


def test_latest_measurement_in(db):
    """Test for latest measurement."""
    date = tools.utcnow()
    ldate = queries.latest_datapoint(db.df, date)
    latest = ldate.index[0]
    assert (latest.year, latest.month, latest.day) == (2022, 12, 31)
    assert (latest.hour, latest.minute, latest.second) == (23, 00, 00)
    assert latest.microsecond == 0
    assert latest.tzinfo == tz.utc
    assert ldate.temperature[0] == 14.7
    assert ldate.wind[0] == 12.9


def test_latest_measurement_context_outside_of(db):
    """Test for queries with a date object outside of historical data."""
    date = dt(year=1922, month=2, day=2, hour=15, minute=2, tzinfo=tz.utc)
    df = queries.latest_datapoint(db.df, date)
    assert df.index.size == 0
    assert df.size == 0


def test_latest_measurement_timzone_difference(db):
    """Test if the timezone difference is considered for the query."""
    date = tools.utcnow()
    latest = queries.latest_datapoint(db.df, date).index[0]
    cest = tz(td(hours=2))
    berlin = latest.replace(tzinfo=cest)
    latest_relative = queries.latest_datapoint(db.df, berlin).index[0]
    assert latest_relative != latest


@pytest.mark.long
def test_queries_considering_timezones(db):
    before = db.df[(db.df.index.month == 1) & (db.df.index.year == 2022)].mean()
    db.df.index = db.df.index.map(lambda x: x.astimezone(7200))
    after = db.df[(db.df.index.month == 1) & (db.df.index.year == 2022)].mean()
    assert before["temperature"] != after["temperature"]
    assert before["wind"] != after["wind"]


test_last_month = [(2, 2022, 1, 31), (1, 2023, 12, 31)]


@pytest.mark.parametrize("month,year,premonth,premonth_days", test_last_month)
def test_last_month(month, year, premonth, premonth_days, db):
    now = tools.utcnow()
    context = now.replace(month=month, year=year)
    selection = queries.last_month(db.df, date=context)
    expected = db.df[db.df.index.month == premonth]

    assert expected.index.size == selection.index.size
    assert selection.index.size == 24 * premonth_days
    assert selection.equals(expected)


def test_specific_month(db):
    now = tools.utcnow().replace(year=2022)
    expected = db.df[db.df.index.month == 1]
    selection = queries.specific_month(db.df, now, 1)
    assert selection.equals(expected)


def test_windowed_selection(db):
    expected = db.df[db.df.index.month == 1]
    start = dt(year=2022, month=1, day=1, tzinfo=tz(td(0)))
    end = dt(year=2022, month=2, day=1, tzinfo=tz(td(0))) - td(seconds=1)
    selection = queries._windowed_selection(db.df, start, end)
    assert selection.equals(expected)


def test_windowed_selection_end_is_included(db):
    expected = db.df[db.df.index.month == 1]
    start = dt(year=2022, month=1, day=1, tzinfo=tz(td(0)))
    end = dt(year=2022, month=2, day=1, tzinfo=tz(td(0)))
    selection = queries._windowed_selection(db.df, start, end)
    assert selection.index.size - 1 == expected.index.size
    assert selection.index.max().month == 2


def test_last_year(db):
    now = tools.utcnow()
    expected = db.df[db.df.index.year == 2022]
    db.df.loc[now] = [2, 2]
    assert expected.index.size == db.index.size - 1
    selection = queries.last_year(db.df, now.replace(year=2023))
    assert selection.equals(expected)


def test_last_week(db):
    date = dt(year=2023, month=1, day=1, tzinfo=tz(td(0)))
    selection = queries.last_week(db.df, date)
    assert selection.index.size == 7 * 24
    assert selection.index.min().day == 25
