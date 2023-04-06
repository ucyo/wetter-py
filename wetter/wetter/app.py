"""Command line tool for accessing the wetter library.

Setup of the command line tool (CLI) for the library.
The user should be able to handle all necessary communication with
the backend using this interface incl. updating of the database.
"""
import argparse
import logging
from datetime import datetime as dt
from datetime import timedelta

from wetter import __version__
from wetter.backend import queries as qu
from wetter.backend.extern import OpenMeteoArchiveMeasurements
from wetter.config import config
from wetter.config.defaults import WETTER_LOG_VARIABLE
from wetter.tools import get_env_logging, logio
from wetter.tools import now as local_now
from wetter.tools import setup_logging, utcnow

setup_logging(get_env_logging(WETTER_LOG_VARIABLE))
log = logging.getLogger(__name__)


def main():
    """Parse user query and and pretty print answer from the database."""
    log.info("Starting main application")
    args = parse_args()
    current_config = config.Configuration()
    db = current_config.get_store()
    now = local_now()
    latest = qu.latest_datapoint(db.df, now)

    if args.cmd == "update":
        if args.historical:
            now = utcnow()
            start = dt(year=now.year - 1, month=1, day=1, tzinfo=now.tzinfo)
            end = now - timedelta(days=30)
            db.update(start=start, end=end, api=OpenMeteoArchiveMeasurements)
        log.info("Update requested")
        db.update()
        config.to_store(db)
    elif args.cmd == "compare":
        log.info("Comparison requested")
        if args.week:
            average = qu.last_week(db.df, now)
            pretty_print_comparison(latest=latest, average=average, mode="week")
        if args.month:
            average = qu.last_month(db.df, now)
            pretty_print_comparison(latest=latest, average=average, mode="month")
        if args.year:
            average = qu.last_year(db.df, now)
            pretty_print_comparison(latest=latest, average=average, mode="year")
        if args.detailed:
            average = qu.specific_month(df=db.df, date=now, month=args.detailed)
            pretty_print_detailed_comparison(average)
    elif args.cmd == "latest":
        log.info("Latest measurement requested")
        pretty_print_latest(latest)
    elif args.cmd == "configure":
        log.info("Configuration information requested")
        if args.systemd:
            current_config._print_systemd_service()
        elif args.systemdtimer:
            current_config._print_systemd_timer()
        elif args.config:
            print("Configuration path:", current_config.config_path)
    else:
        log.err(f"KeyError: Can not understand the provided subcommand {args.cmd}", exc_info=True)


@logio(log)
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
    yearcomb = subparsers.add_parser("update", help="Update DB")
    yearcomb.add_argument("--historical", action="store_true", help="Update with historical data")
    comparison_parser = subparsers.add_parser("compare", help="Compare w/ last week, month, year")
    group = comparison_parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--last-week", action="store_true", dest="week", help="Compare w/ last week")
    group.add_argument("--last-year", action="store_true", dest="year", help="Compare w/ last year")
    group.add_argument("--last-month", action="store_true", dest="month", help="Compare w/ last month")
    group.add_argument("--month", type=int, choices=range(1, 13), dest="detailed", help="Month")
    confparser = subparsers.add_parser("configure", help="Configuration of the tool")
    gconf = confparser.add_mutually_exclusive_group(required=True)
    gconf.add_argument("--systemd", action="store_true", help="Show systemd profile")
    gconf.add_argument("--systemdtimer", action="store_true", help="Show systemd timer profile")
    gconf.add_argument("--config", action="store_true", help="Show configuration path")
    return parser


@logio(log)
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
        log.info(f"No subcommand given, setting to {args.cmd}")
    return args


def pretty_print_latest(latest):
    """Pretty print the output of the latest measurement.

    :params latest: Latest measurement from database
    :type latest: pd.DataFrame
    :raises: IndexError
    """
    try:
        t_now = latest.temperature[0]
        w_now = latest.wind[0]
    except IndexError as err:
        log.error(f"IndexError: {err}", exc_info=True)
        print("Unfortunately there are not enough data points.")
        print("Please consider updating the database: 'wetter update'")
    else:
        msg = f"Currently it is 🌡️ {t_now:.1f}°C and wind speed 🌬️ {w_now:.1f} km/h."
        print(msg)
        log.info(msg)
        print_disclaimer_latest(latest)


def pretty_print_comparison(latest, average, mode, variable="temperature"):
    """Pretty print the output of a comparison query.

    :params latest: Latest measurement from database
    :type latest: pd.DataFrame
    :params average: Average measurements of a certain time window
    :type average: pd.DataFrame
    :params mode: Window definition either 'week','month' or 'year'
    :type mode: str
    :raises: AssertionError, IndexError
    """
    mode = mode.lower()
    assert mode in ("week", "year", "month"), f"Mode {mode} is unknown."

    try:
        temp_avg = average[variable][0]
        temp_now = latest[variable][0]
    except IndexError as err:
        log.error(f"IndexError: {err}", exc_info=True)
        print("Unfortunately there are not enough data points.")
        add = "--historical" if mode == "year" else ""
        print(f"Please consider updating the database: `wetter update {add}`")
    else:
        diff = temp_avg - temp_now
        relation = "colder" if diff < 0 else "warmer"
        relation = "same" if diff == 0 else relation

        msg = f"It was on average {diff:.1f}°C {relation} last {mode} ({temp_avg:.1f}°C) then today ({temp_now:.1f}°C)"
        print(msg)
        log.info(msg)
        print_disclaimer_window(average)


def pretty_print_detailed_comparison(window, variable="temperature"):
    """Pretty print the output of a detailed month window comparison.

    :params window: Measurement within a certain month
    :type latest: pd.DataFrame
    :raises: AssertionError, IndexError, KeyError
    """
    try:
        assert window.index.size != 0, "Window length must be > 0."
    except AssertionError as err:
        log.error(f"AssertionError: {err}", exc_info=True)
        print("Unfortunately there are not enough data points.")
        print("Please consider updating the database: `wetter update`")
    else:
        window.index = window.index.map(lambda x: x.astimezone(local_now().tzinfo))
        overall_average = window.mean()[variable]
        daily_average = {data.index[0]: data.mean()[variable] for (day, data) in window.groupby(window.index.day)}
        hotter_days = {k: v for k, v in daily_average.items() if v > overall_average}
        month = window.index[0].strftime("%B %Y")
        msg = f"It was on average 🌡️ {overall_average:.1f}°C in 📅 {month}."
        print(msg)
        log.info(msg)
        print(f"The following {len(hotter_days)} days were hotter 🔥 than the average:")
        for day, temp in hotter_days.items():
            day_str = day.strftime("%Y-%m-%d")
            print(f"{day_str} @ {temp:.1f}°C")
        log.info(f"Hotter days are: {hotter_days}")


def print_disclaimer_latest(latest):
    """Disclaimer about the data the calculations are based upon.

    :params latest: Latest measurement from database
    :type latest: pd.DataFrame
    :raises: AssertionError
    """
    try:
        assert latest.index.size > 0, "There are no measurements in the database."
    except AssertionError as err:
        log.error(f"AssertionError: {err}", exc_info=True)
        print("Unfortunately there are not enough data points.")
        print("Please consider updating the database: `wetter update`")
    else:
        latest.index = latest.index.map(lambda x: x.astimezone(local_now().tzinfo))
        date = latest.index[0].strftime("%Y-%m-%d")
        time = latest.index[0].strftime("%I:%M%p")
        disclaimer = f"Latest measurement on 📅 {date} @ {time}."
        print(disclaimer)


def print_disclaimer_window(window):
    """Disclaimer about the data the calculations are based upon.

    :params window: Measurement within a certain month
    :type latest: pd.DataFrame
    """
    num = window.index.size
    try:
        assert num > 0, "Window is not allowed to be empty."
    except AssertionError as err:
        log.error(f"AssertionError: {err}", exc_info=True)
        print("Unfortunately there are not enough data points.")
        print("Please consider updating the database: `wetter update`")
    else:
        window.index = window.index.map(lambda x: x.astimezone(local_now().tzinfo))
        start = window.index.min().strftime("%Y-%m-%d")
        end = window.index.max().strftime("%Y-%m-%d")

        disclaimer = f"Average was calculated using #{num} measurements between 📅 {start} - {end}."
        print(disclaimer)


if __name__ == "__main__":
    main()
