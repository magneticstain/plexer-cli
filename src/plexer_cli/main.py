#!/usr/bin/env python3
"""
Plexer - Normalize media files for use with Plex Media Server

Main App Entrypoint
"""

__author__ = "magneticstain"
__version__ = "0.0.3-5"
__license__ = "MIT"

import argparse
import logzero
from logzero import logger
# yes, docs suggest importing it twice:
# https://logzero.readthedocs.io/en/latest/#advanced-usage-examples

from plexer_cli.file_manager import FileManager

def fetch_cli_args() -> argparse.Namespace:
    """Parse CLI arguments passed to the application during startup"""

    parser = argparse.ArgumentParser()

    parser.add_argument("--version", action="version", version=f"{__version__}")

    parser.add_argument("-s", "--source-dir", action="store", required=True)
    parser.add_argument("-d", "--destination-dir", action="store", required=True)

    return parser.parse_args()


def main():
    """Main entry point of the app"""

    cli_args = fetch_cli_args()

    # logzero.json(enable=True)
    logzero.loglevel(logzero.DEBUG)
    logzero.logfile(None)

    logger.info("starting Plexer")
    logger.debug("options: %s", cli_args)

    fm = FileManager(src_dir=cli_args.source_dir, dst_dir=cli_args.destination_dir)

    # get and prep artifacts for processing
    logger.debug("prepping artifacts for processing")
    artifacts = fm.prep_artifacts(artifacts=fm.get_artifacts())
    logger.info("%d artifact(s) found in source directory", len(artifacts))

    logger.info("processing artifacts")
    fm.process_directory(dir_artifacts=artifacts)
    logger.info("artifact processing completed successfully")
