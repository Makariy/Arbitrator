import sys

from lib.argparser import main_parser, tracker_parser
from lib.logging import configure_logging


def main(args):
    args, extra = args
    if args.command == "track":
        from layers.tracker.tracker import run_tracker
        args = tracker_parser.parse_args(extra)
        run_tracker(args)


if __name__ == "__main__":
    configure_logging()

    arguments = main_parser.parse_known_args(sys.argv)
    main(arguments)
