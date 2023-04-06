"""This module defines opinionated defaults for certain information."""
import os
import platform as pl

import platformdirs

WETTER_LOG_VARIABLE = "WETTER_LOG"

APPNAME = "wetter"
APPAUTHOR = "ucyo"
DEFAULT_LAT = 49
DEFAULT_LON = 8.41

BASE_CONFIG = {"location": {"lat": DEFAULT_LAT, "lon": DEFAULT_LON}}

BASE_STORE = {
    "lat": DEFAULT_LAT,
    "lon": DEFAULT_LON,
    "version": 1,
    "data": {
        "index": ["temperature", "wind"],
        "columns": [
            "2023-01-01T00:00:00.000000+0000",
            "2023-01-01T01:00:00.000000+0000",
        ],
        "data": [[7.7, 12.7], [6.8, 13.0]],
    },
}

USER = os.environ.get("USER", os.environ.get("USERNAME"))

SYSTEMD_SERVICE = """[Unit]
Description=Update of wetter cli tool using systemd
Wants=wetter.timer

[Service]
Type=oneshot
ExecStart=/usr/bin/wetter update
User={0}

[Install]
WantedBy=multi-user.target
""".format(
    USER
)

SYSTEMD_TIMER = """[Unit]
Description=Update of wetter cli tool using systemd

[Timer]
OnCalendar=*-*-* *:05:05

[Install]
WantedBy=timers.target
"""


def get_config_path():
    if pl.system().lower() == "linux":
        return os.path.join(platformdirs.user_config_dir(appname=APPNAME), f"{APPNAME}.toml")
    else:
        return os.path.join(
            platformdirs.user_data_dir(appname=APPNAME, appauthor=APPAUTHOR),
            f"{APPNAME}.toml",
        )


DEFAULT_CONFIG_PATH = get_config_path()
