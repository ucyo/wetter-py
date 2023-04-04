"""Test file for the backend connection.

the functions in this file are being used to test the backend service
of the application. It is responsible for the following tasks:

- Testing the structure of the data being saved as json
- Testing the communication to weather APIs
- Testing the update process
"""
# import os
from datetime import datetime as dt

import pandas as pd
import pytest

from wetter.config import Configuration
from wetter import conn


@pytest.fixture
def db():
    db = Configuration().get_store()
    yield db.df


def test_connection_returns_df(db):
    assert isinstance(db, pd.DataFrame)


def test_correct_naming(db):
    assert "temperature" in db.columns
    assert "wind" in db.columns
    assert isinstance(db.index[0], dt)


def test_db_has_no_empty_values(db):
    assert db.isna()._values.sum() == 0


# @pytest.mark.web
# def test_update():
#     filename = os.path.join(conn.DATA_LOCATION, "test.json")
#     old = conn.WetterDB(filename).df
#     new = conn.WetterDB.update(filename, dry_run=True)
#     assert new.size >= old.size


@pytest.mark.web
def test_to_old():
    start = dt(year=1201, month=1, day=1)
    end = dt.now()
    qt = conn.QueryTicket(start=start, end=end, lat=49, lon=8.41)

    assert conn.OpenMeteoMeasurements.get(qt).status_code != 200


def test_query_ticket_reversed_dates():
    end = dt.now()
    start = dt.now()
    qt = conn.QueryTicket(start=start, end=end, lat=49, lon=8.41)
    assert qt.end == start
    assert qt.start == end
