import logging


logger = logging.getLogger(__package__)


def run_tracker(args):
    input = args.input
    output = args.output

    logger.info(f"Tracking from {input} to {output}")
