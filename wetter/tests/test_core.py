from wetter import core
from wetter import conn

def test_latest_measurement():
    data = conn.get_db()
    df = core.latest_datapoint()
    assert df.index.size == 1
    # TODO: Check what the value is
