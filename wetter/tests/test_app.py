"""Test file for the command line tool.

Checking the functionality of the application and possible input mistakes.
It is responsible for the following tasks:

- Catching of unallowed commands
- Expected default behviour application if variables/commands are forgotten
"""
from argparse import ArgumentParser

import pytest

from wetter import app


def test_get_parser():
    p = app.get_parser()
    assert isinstance(p, ArgumentParser)


def test_empty():
    args = app.parse_args([])
    assert args.cmd == "latest"


def test_compare():
    with pytest.raises(SystemExit):
        app.parse_args(["compare"])
