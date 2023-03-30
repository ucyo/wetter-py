from wetter import conn
import pandas as pd


def test_connection_returns_df():
    data = conn.get_db()
    assert isinstance(data, pd.DataFrame)


def test_db_has_no_empty_values():
    data = conn.get_db()
    assert data.isna()._values.sum() == 0
