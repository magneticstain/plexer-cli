# Plexer

<!-- reenable once issue #27 is complete -->
<!-- ![GitHub Release](https://img.shields.io/github/v/release/magneticstain/plexer?include_prereleases) -->
![PyPI - Version](https://img.shields.io/pypi/v/plexer-cli)

![GitHub License](https://img.shields.io/github/license/magneticstain/plexer)
![Supported Python Versions](https://img.shields.io/python/required-version-toml?tomlFilePath=https%3A%2F%2Fraw.githubusercontent.com%2Fmagneticstain%2Fplexer%2Frefs%2Fheads%2Fmain%2Fpyproject.toml)

![GitHub Issues or Pull Requests](https://img.shields.io/github/issues/magneticstain/plexer)
![GitHub Downloads (all assets, all releases)](https://img.shields.io/github/downloads/magneticstain/plexer/total)

[![OpenSSF Scorecard](https://api.scorecard.dev/projects/github.com/magneticstain/plexer/badge)](https://scorecard.dev/viewer/?uri=github.com/magneticstain/plexer)
[![Codacy Badge](https://app.codacy.com/project/badge/Grade/38b2a65ed9ac4c85afc98e259d73474f)](https://app.codacy.com/gh/magneticstain/plexer/dashboard?utm_source=gh&utm_medium=referral&utm_content=&utm_campaign=Badge_grade)

[![Run Full Suite of Checks and Tests](https://github.com/magneticstain/plexer/actions/workflows/run_full_test_suite.yml/badge.svg)](https://github.com/magneticstain/plexer/actions/workflows/run_full_test_suite.yml)
[![Release](https://github.com/magneticstain/plexer/actions/workflows/release.yml/badge.svg)](https://github.com/magneticstain/plexer/actions/workflows/release.yml)

## Summary

A CLI tool made to make organizing your media for [Plex Media Server](https://www.plex.tv/) easy. Normalize names of media files and directories to match [the hierarchial requirements that Plex requires](https://support.plex.tv/articles/naming-and-organizing-your-movie-media-files/).

## Features

### Support

Currently, Plexer only supports organizing movies and other individual video files.

### Roadmap

- [ ] Support for TV Shows ([#28](https://github.com/magneticstain/plexer/issues/28))
- [ ] Docker implementations ([#29](https://github.com/magneticstain/plexer/issues/29))
- [ ] MacOS support ([#30](https://github.com/magneticstain/plexer/issues/30))
- [ ] Windows support ([#31](https://github.com/magneticstain/plexer/issues/31))
- [ ] Metadata inference using file/directory info (i.e. analyze the video files to "guess" what the name, year, etc is) ([#32](https://github.com/magneticstain/plexer/issues/32))

## Install

To install plexer, us pip/[pipx](https://github.com/pypa/pipx)/[pipenv](https://pipenv.pypa.io/en/latest/)/your favorite build front-end to install the `plexer-cli` package.

```bash
pip install plexer-cli
```

## Requirements

### Media Metadata

The most important requirement before running plexer is to ensure that you've created a `.plexer` file in each of your target directories.

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

[![Hatch project](https://img.shields.io/badge/%F0%9F%A5%9A-Hatch-4051b5.svg)](https://github.com/pypa/hatch)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

For developing with Plexer, there are several tools that are in use:

1. Build Backend, Packaging, and Dependency Management:
   1. [Hatch](https://hatch.pypa.io/1.12/)
1. Analysis Tools:
   1. [Ruff](https://docs.astral.sh/ruff/)
   1. [Codacy](https://app.codacy.com/gh/magneticstain/plexer/dashboard)
1. Testing:
   1. [Pytest](https://docs.pytest.org/en/latest/)
   1. [Tox](https://tox.wiki/en/stable/)
