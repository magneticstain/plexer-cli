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

# traverse all **directories** in src dir
# for each dir:
#   prompt user for naming slug
#   traverse both dirs and files
#   if file is media file, rename to <slug>.<ext>
#   else rm file
#   move dir to dst dir and rename to <slug>


def main(cli_args):
    """ Main entry point of the app """

    logzero.json(enable=True)
    logzero.loglevel(logzero.DEBUG)
    logzero.logfile(None)

    logger.info("starting Plexer")
    logger.info("options: %s", cli_args)

    logger.info("reading source directory")
    fm = FileManager()
    artifacts = fm.get_artifacts(cli_args.source_dir)

    print(artifacts)


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
