from wetter import conn
import pandas as pd
from datetime import datetime


def test_connection_returns_df():
    data = conn.get_db()
    assert isinstance(data, pd.DataFrame)


def test_correct_namin():
    data = conn.get_db()
    assert "temperature" in data.columns
    assert "wind" in data.columns
    assert "wmo" in data.columns
    assert isinstance(data.index[0], datetime)


def test_db_has_no_empty_values():
    data = conn.get_db()
    assert data.isna()._values.sum() == 0
