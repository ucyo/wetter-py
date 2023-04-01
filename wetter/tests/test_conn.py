import os
from datetime import datetime as dt

import pandas as pd
import pytest

from wetter import conn


@pytest.fixture
def db():
    db = conn.get_db()
    yield db.df


def test_connection_returns_df(db):
    assert isinstance(db, pd.DataFrame)


def test_correct_naming(db):
    assert "temperature" in db.columns
    assert "wind" in db.columns
    assert isinstance(db.index[0], dt)


def test_db_has_no_empty_values(db):
    assert db.isna()._values.sum() == 0


@pytest.mark.web
def test_update():
    filename = os.path.join(conn.DATA_LOCATION, "test.json")
    old = conn.WetterDB(filename).df
    new = conn.WetterDB.update(filename, dry_run=True)
    assert new.size >= old.size


@pytest.mark.web
def test_to_old():
    start = dt(year=1201, month=1, day=1)
    end = dt.now()
    qt = conn.QueryTicket(start=start, end=end)

    with pytest.raises(Exception):
        conn.OpenMeteoMeasurements.get(qt)


def test_query_ticket_reversed_dates():
    end = dt.now()
    start = dt.now()
    qt = conn.QueryTicket(start=start, end=end)
    assert qt.end == start
    assert qt.start == end
