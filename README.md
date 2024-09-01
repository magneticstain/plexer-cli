# Plexer

Normalize media files for use with Plex Media Server.

[![Hatch project](https://img.shields.io/badge/%F0%9F%A5%9A-Hatch-4051b5.svg)](https://github.com/pypa/hatch)
[![linting: pylint](https://img.shields.io/badge/linting-pylint-yellowgreen)](https://github.com/pylint-dev/pylint)

## Requirements

### Software Dependencies

Start by creating a virtual environment and installing the required packages. Typically that looks something like:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Media Metadata

The biggest requirement before running plexer is to ensure that you've created a `.plexer` file in each of your target directories.

This is a JSON-formatted file that includes the movie metadata required by Plexer to perform its jobs.

#### Plexer File Generator

To easily create the `.plexer` file, you can use the one-liner below while in the movie's directory:

```bash
echo -n "Media Name: ";read MEDIA_NAME;echo -n "Release Year (YYYY): ";read RELEASE_YEAR;echo "{\"name\": \"${MEDIA_NAME}\", \"release_year\": \"${RELEASE_YEAR}\"}" > .plexer
```

It can be modified to support different types of media as well.

## Usage

The source directory is the directory containing the raw media. The destination is where you'd like to save the processed media to.

```text
usage: plexer.py [-h] [-v] [--version] -s SOURCE_DIR -d DESTINATION_DIR

options:
  -h, --help            show this help message and exit
  -v, --verbose         Verbosity (-v, -vv, etc)
  --version             show program's version number and exit
  -s SOURCE_DIR, --source-dir SOURCE_DIR
  -d DESTINATION_DIR, --destination-dir DESTINATION_DIR
```
