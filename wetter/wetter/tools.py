"""Helper functions for the mainteanance of the library

Most of these functions are in one way or the other helping out w/ DRY principles.
They are not functions specifically designed for this package and can
easily fit in other packages.
"""
import functools
import logging
import os
import time
from datetime import datetime as dt
from datetime import timezone as tz
from logging import handlers

import platformdirs
import pytz

from wetter.config.defaults import APPAUTHOR, APPNAME


def logio(logger, level="debug"):
    """Decorator for logging input/output of functions.

    :param logger: Python logger to be used
    :type logger: logging.Logger
    :param level: Logging level of logs
    :type level: str
    """

    def dec_logio(func):
        @functools.wraps(func)
        def wrapper_func(*args, **kwargs):
            getattr(logger, level)(f"Call: {func.__name__}()")
            getattr(logger, level)(f"Args: {args}")
            getattr(logger, level)(f"Kwargs: {kwargs}")
            result = func(*args, **kwargs)
            getattr(logger, level)(f"Result: {result}")
            return result

        return wrapper_func

    return dec_logio


def setup_logging(level=logging.INFO, max_bytes=10 * 1024 * 1024, backups=10):
    """Setting up the logging environment.

    :param level: Logging level
    :type level: int (best use proper level e.g. logging.INFO)
    :param max_bytes: Maximum file size of log in bytes
    :type max_bytes: int
    :param backups: Number of rotation files for logs
    :type backups: int
    """
    log_path = os.path.join(
        platformdirs.user_log_dir(appname=APPNAME, appauthor=APPAUTHOR),
        f"{APPNAME}.log",
    )
    os.makedirs(os.path.dirname(log_path), exist_ok=True)
    handler = handlers.RotatingFileHandler(log_path, maxBytes=max_bytes, backupCount=backups)
    formatter = logging.Formatter("%(name)s %(asctime)s %(levelname)s %(message)s")
    handler.setFormatter(formatter)
    logging.basicConfig(handlers=[handler], level=level)
    # debug, info, warning, error, critical


def utcnow():
    """Return current UTC time (with timezone information)."""
    return dt.utcnow().replace(tzinfo=tz.utc)


def now():
    """Return current local time (with timezone information)."""
    utc_offset = -time.altzone if time.daylight else -time.timezone
    return dt.now().replace(tzinfo=pytz.FixedOffset(utc_offset / 60))


def get_env_logging(env_key):
    """Return logging level based on povided environment variable.

    :param env_key: Environment variable to check upon
    :type env_key: str
    :return: Logging level [default: WARNING]
    :rtype: logging.Level
    """
    env_val = os.environ.get(env_key, logging.WARNING)
    levels = {
        "critical": logging.CRITICAL,
        "error": logging.ERROR,
        "warn": logging.WARNING,
        "warning": logging.WARNING,
        "info": logging.INFO,
        "debug": logging.DEBUG,
    }
    if isinstance(env_val, str) and env_val in levels.keys():
        env_val = levels[env_val]
    return env_val
