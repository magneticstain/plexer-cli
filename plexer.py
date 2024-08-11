#!/usr/bin/env python3
"""
Plexer - Normalize media files for use with Plex Media Server
"""

__author__ = "magneticstain"
__version__ = "0.1.0"
__license__ = "MIT"

import argparse
import logzero
from logzero import logger
# yes, docs suggest importing it twice:
# https://logzero.readthedocs.io/en/latest/#advanced-usage-examples

from plexer.file_manager import FileManager

def main(cli_args):
    """ Main entry point of the app """

    # logzero.json(enable=True)
    logzero.loglevel(logzero.DEBUG)
    logzero.logfile(None)

    logger.info("starting Plexer")
    logger.debug("options: %s", cli_args)

    fm = FileManager(src_dir=cli_args.source_dir, dst_dir=cli_args.destination_dir)

    logger.info("reading source directory")
    artifacts = fm.get_artifacts()
    logger.info("%d artifact(s) found in source directory", len(artifacts))

    logger.info("processing artifacts")
    fm.process_directory(dir_artifacts=artifacts)
    logger.info("artifact processing completed successfully ")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "-v",
        "--verbose",
        action="count",
        default=0,
        help="Verbosity (-v, -vv, etc)"
    )

    parser.add_argument(
        "--version",
        action="version",
        version=f"{__version__}"
    )

    parser.add_argument("-s", "--source-dir", action="store", required=True)
    parser.add_argument("-d", "--destination-dir", action="store", required=True)

    args = parser.parse_args()

    main(args)
