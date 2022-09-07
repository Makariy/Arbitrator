import sys

from lib.argparser import main_parser, tracker_parser
from lib.logging import configure_logging
from layers.tracker.tracker import run_trackers, create_tracker

import config


def main(args):
    args, extra = args
    if args.command == "track":
        run_trackers([create_tracker(to_track) for to_track in config.TO_TRACK])


if __name__ == "__main__":
    configure_logging()

    arguments = main_parser.parse_known_args(sys.argv)
    main(arguments)
