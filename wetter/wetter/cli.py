"""Command line tool for accessing the wetter library.

Setup of the command line tool (CLI) for the library.
The user should be able to handle all necessary communication with
the backend using this interface incl. updating of the database.
"""

import argparse

from wetter import conn
from wetter import queries as qu

from . import __version__


def main():
    """Parse user query and and pretty print answer from the database."""
    args = parse_args()
    db = conn.get_db()
    now = conn.now()
    latest = qu.latest_datapoint(db.df, now)

    if args.cmd == "update":
        conn.WetterDB.update(conn.DB)
        print("Update successful!")
    elif args.cmd == "compare":
        if args.week:
            average = qu.last_week(db.df, now)
            pretty_print_comparison(latest=latest, average=average, mode="week")
        if args.month:
            average = qu.last_month(db.df, now)
            pretty_print_comparison(latest=latest, average=average, mode="month")
        if args.year:
            average = qu.last_year(db.df, now)
            pretty_print_comparison(latest=latest, average=average, mode="year")
    elif args.cmd == "compare-details":
        average = qu.specific_month(db.df, now, args.month)
        pretty_print_detailed_comparison(average)
    elif args.cmd == "latest":
        pretty_print_latest(latest)
    else:
        raise Exception(f"Can not understand the provided subcommand {args.cmd}")


def get_parser():
    """Define argument parser for CLI tool."""
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


def parse_args(args=None):
    """Parse arguments from the command line.

    This is a wrapper around the `argparse` argument parser.
    It is necessary since `argparse` does not allow to setup a default subcommand.
    Should the subcommand be empty, this function will fill in the `latest` subcommand.

    :param args: Arguments to be parsed
    :type args: list
    :return: Parsed arguments
    :rtype: `argparse.Namespace`
    """
    parser = get_parser()
    if args is None:
        args = parser.parse_args()
    else:
        args = parser.parse_args(args)
    if args.cmd is None:
        args.cmd = "latest"
    return args


def pretty_print_latest(latest):
    """Pretty print the output of the latest measurement.

    :params latest: Latest measurement from database
    :type latest: pd.DataFrame
    """
    t_now = latest.temperature[0]
    w_now = latest.wind[0]
    msg = f"Currently it is 🌡️ {t_now:.1f}°C and windspeed 🌬️ {w_now:.1f} km/h."
    print(msg)
    # print_disclaimer_latest(latest)


def pretty_print_comparison(latest, average, mode):
    """Pretty print the output of a comparison query.

    :params latest: Latest measurement from database
    :type latest: pd.DataFrame
    :params average: Average measurements of a certain time window
    :type average: pd.DataFrame
    :params mode: Window definition either 'week','month' or 'year'
    :type mode: str
    """
    mode = mode.lower()
    assert mode in ("week", "year", "month")
    variable = "temperature"

    temp_avg = average[variable][0]
    temp_now = latest[variable][0]
    diff = temp_avg - temp_now
    relation = "colder" if diff < 0 else "warmer"
    relation = "same" if diff == 0 else relation

    msg = f"It was on average {diff:.1f}°C {relation} last {mode} ({temp_avg:.1f}°C) then today ({temp_now:.1f}°C)"
    print(msg)
    # print_disclaimer_window(average)


def pretty_print_detailed_comparison(window):
    """Pretty print the output of a detailed month window comparison.

    :params window: Measurement within a certain month
    :type latest: pd.DataFrame
    """
    window.index = window.index.map(lambda x: x.astimezone(conn.now().tzinfo))
    variable = "temperature"
    overall_average = window.mean()[variable]
    daily_average = {data.index[0]: data.mean()[variable] for (day, data) in window.groupby(window.index.day)}
    hotter_days = {k: v for k, v in daily_average.items() if v > overall_average}

    month = window.index[0].strftime("%B %Y")
    msg = f"It was on average 🌡️ {overall_average:.1f}°C in 📅 {month}."
    print(msg)
    print(f"The following {len(hotter_days)} days were hotter 🔥 than the average:")
    for day, temp in hotter_days.items():
        day_str = day.strftime("%Y-%m-%d")
        print(f"{day_str} @ {temp:.1f}°C")
    # print_disclaimer_window(window)


def print_disclaimer_latest(latest):
    """Disclaimer about the data the calculations are based upon.

    :params latest: Latest measurement from database
    :type latest: pd.DataFrame
    """
    latest.index = latest.index.map(lambda x: x.astimezone(conn.now().tzinfo))
    date = latest.index[0].strftime("%Y-%m-%d")
    time = latest.index[0].strftime("%I:%M%p")
    disclaimer = f"Latest measurement on 📅 {date} @ {time}."
    print(disclaimer)


def print_disclaimer_window(window):
    """Disclaimer about the data the calculations are based upon.

    :params window: Measurement within a certain month
    :type latest: pd.DataFrame
    """
    window.index = window.index.map(lambda x: x.astimezone(conn.now().tzinfo))
    num = window.index.size
    start = window.index.min().strftime("%Y-%m-%d")
    end = window.index.max().strftime("%Y-%m-%d")

    disclaimer = f"Average was calculated using #{num} measurements between 📅 {start} - {end}."
    print(disclaimer)


if __name__ == "__main__":
    main()
