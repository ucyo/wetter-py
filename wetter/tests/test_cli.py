from argparse import ArgumentParser

from wetter import cli


def test_get_parser():
    p = cli.get_parser()
    assert isinstance(p, ArgumentParser)


def test_empty():
    p = cli.get_parser()
    args = p.parse_args([])
    assert args.cmd is None
