from argparse import ArgumentParser

from wetter import cli


def test_get_parser():
    p = cli.get_parser()
    assert isinstance(p, ArgumentParser)


def test_empty():
    args = cli.parse_args([])
    assert args.cmd is "latest"

def test_compare():
    with pytest.raises(SystemExit):
        args = cli.parse_args(["compare"])
