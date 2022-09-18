import sys

from lib.argparser import main_parser
from lib.logging import configure_logging
from layers.tracker.tracker import run_trackers
from layers.analyzer.analyzer import run_analyzer
from bot.bot import run_bot

import config


def main(args):
    args, extra = args
    if args.command == "track":
        run_trackers(config.TO_TRACK)
    if args.command == "analyze":
        run_analyzer()
    if args.command == "bot":
        run_bot()


if __name__ == "__main__":
    configure_logging()

    arguments = main_parser.parse_known_args(sys.argv)
    main(arguments)
