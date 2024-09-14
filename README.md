# Plexer

Normalize media files for use with Plex Media Server.

[![Hatch project](https://img.shields.io/badge/%F0%9F%A5%9A-Hatch-4051b5.svg)](https://github.com/pypa/hatch)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

[![Codacy Badge](https://app.codacy.com/project/badge/Grade/38b2a65ed9ac4c85afc98e259d73474f)](https://app.codacy.com/gh/magneticstain/plexer/dashboard?utm_source=gh&utm_medium=referral&utm_content=&utm_campaign=Badge_grade)

![GitHub Issues or Pull Requests](https://img.shields.io/github/issues/magneticstain/plexer)
![GitHub Downloads (all assets, all releases)](https://img.shields.io/github/downloads/magneticstain/plexer/total)

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

## Development

### Software Stack

For developing with Plexer, there are several tools that are in use:

1. Build Backend:
   1. [Hatch](https://hatch.pypa.io/1.12/)
1. Analysis Tools:
   1. [Ruff](https://docs.astral.sh/ruff/)
   1. [Codacy](https://app.codacy.com/gh/magneticstain/plexer/dashboard)
1. Testing:
   1. [Pytest](https://docs.pytest.org/en/latest/)
   1. [Tox](https://tox.wiki/en/stable/)
