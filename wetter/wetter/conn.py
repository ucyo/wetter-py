import pandas as pd
from datetime import datetime
import os

DATA_LOCATION = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data")
DB = os.path.join(DATA_LOCATION, "OpenMeteo.json")


def get_db():
    _raw_data = pd.read_json(DB)
    df = pd.DataFrame(
        {
            "time": [
                datetime.strptime(x, "%Y-%m-%dT%H:%M") for x in _raw_data.hourly["time"]
            ],
            "temperature": _raw_data.hourly["temperature_2m"],
            "wind": _raw_data.hourly["windspeed_10m"],
            "wmo": _raw_data.hourly["weathercode"],
        }
    )
    df = df.set_index("time")
    return df
