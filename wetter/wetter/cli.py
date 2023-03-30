import argparse
from . import __version__


def main():
    args = parse_arguments()
    if args.cmd == "update":
        cmd_update()
    elif args.cmd == "compare":
        cmd_compare(args.month)
    else:
        cmd_latest()


def parse_arguments():
    parser = argparse.ArgumentParser(
        prog="wetter",
        description="Cli to check the outside when you're inside",
        epilog="Have a nice day!",
    )
    parser.add_argument("-v", "--version", action="version", version=__version__)
    subparsers = parser.add_subparsers(
        help="Subcommands for updates and details", dest="cmd"
    )
    latest_parser = subparsers.add_parser("latest", help="Latest measurment [default]")
    update_parser = subparsers.add_parser("update", help="Update DB")
    comparison_parser = subparsers.add_parser(
        "compare", help="Compare temperature of specific month"
    )
    comparison_parser.add_argument(
        "month", type=int, choices=range(1, 13), help="Month to be detailed [int]"
    )
    return parser.parse_args()


def cmd_latest():
    print("Print latest measurement")


def cmd_update():
    print("Update DB")


def cmd_compare(month):
    print("Comparison of specific month")
