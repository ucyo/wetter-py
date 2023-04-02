import argparse
from datetime import datetime as dt
from datetime import timezone as tz

from wetter import conn
from wetter import queries as qu

from . import __version__


def main():
    args = parse_args()
    db = conn.get_db()
    now = dt.utcnow().astimezone(tz.utc)

    if args.cmd == "update":
        conn.WetterDB.update(conn.DB)
        print("Updated DB")
    elif args.cmd == "compare":
        if args.week:
            print(qu.last_week(db.df, now))
        if args.month:
            print(qu.last_month(db.df, now))
        if args.year:
            print(qu.last_year(db.df, now))
    elif args.cmd == "compare-details":
        print(qu.specific_month(db.df, now, args.month))
    else:
        print(qu.latest_datapoint(db.df, now))


def get_parser():
    parser = argparse.ArgumentParser(
        prog="wetter",
        description="Cli tool to check the outside when you're inside",
        epilog="Have a nice day!",
    )
    parser.add_argument("-v", "--version", action="version", version=__version__)
    subparsers = parser.add_subparsers(help="Subcommands for updates and details", dest="cmd")
    subparsers.add_parser("latest", help="Latest measurment [default]")
    subparsers.add_parser("update", help="Update DB")
    comparison_parser = subparsers.add_parser("compare", help="Compare w/ last week, month, year")
    group = comparison_parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--last-week", action="store_true", dest="week", help="Compare w/ last week")
    group.add_argument("--last-year", action="store_true", dest="year", help="Compare w/ last year")
    group.add_argument("--last-month", action="store_true", dest="month", help="Compare w/ last month")
    detailed_cmp_parser = subparsers.add_parser("compare-details", help="Compare today w/ specific month")
    detailed_cmp_parser.add_argument("month", type=int, choices=range(1, 13), help="Month")
    return parser

def parse_args(args):
    parser = get_parser()
    args = parser.parse_args(args)
    if args.cmd is None:
        args.cmd = "latest"
    return args
