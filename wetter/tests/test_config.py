import json

import pandas as pd
import pytest

from wetter.config import config
from wetter.config.parser import DecodeDateTime, WetterEncoder


@pytest.fixture
def conf():
    yield config.Configuration(store_path="./tests/testdata.json", self_check=False)


def test_json_datetime_encoder(conf):
    date = conf.get_store().df.index[:1]
    encoded = json.dumps(date[0], cls=WetterEncoder)
    assert encoded == '"2022-01-01T00:00:00.000000+0000"'


def test_json_datetime_decoder(conf):
    js = {"columns": ["2022-01-01T00:00:00.000000+0000"]}
    expected = conf.get_store().df.index[:1]
    result = DecodeDateTime(js)
    assert result["columns"] == expected


def test_load_save_config_with_checks():
    db = config.Configuration(config_path="tests/testconfig.toml", store_path="tests/testdata.json").get_store()
    config.to_store(db)
    new_db = config.Configuration(config_path="tests/testconfig.toml", store_path="tests/testdata.json").get_store()
    assert isinstance(db.df, pd.DataFrame)
    assert new_db.df.equals(db.df)


@pytest.mark.long
def test_load_changed_config_with_checks():
    db = config.Configuration(config_path="tests/testconfig_changed.toml", store_path="tests/testdata.json").get_store()
    assert db.df.size > 0
