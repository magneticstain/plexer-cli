# Plexer

[![GitHub Release](https://img.shields.io/github/v/release/magneticstain/plexer-cli?include_prereleases)](https://github.com/magneticstain/plexer-cli/releases)
[![PyPI - Version](https://img.shields.io/pypi/v/plexer_cli)](https://pypi.org/project/plexer-cli/)

![GitHub License](https://img.shields.io/github/license/magneticstain/plexer-cli)
![Supported Python Versions](https://img.shields.io/python/required-version-toml?tomlFilePath=https%3A%2F%2Fraw.githubusercontent.com%2Fmagneticstain%2Fplexer-cli%2Frefs%2Fheads%2Fmain%2Fpyproject.toml)

![GitHub Issues or Pull Requests](https://img.shields.io/github/issues/magneticstain/plexer-cli)
![GitHub Downloads (all assets, all releases)](https://img.shields.io/github/downloads/magneticstain/plexer-cli/total)

[![OpenSSF Scorecard](https://api.scorecard.dev/projects/github.com/magneticstain/plexer-cli/badge)](https://scorecard.dev/viewer/?uri=github.com/magneticstain/plexer-cli)
[![OpenSSF Best Practices](https://www.bestpractices.dev/projects/13659/badge)](https://www.bestpractices.dev/projects/13659)

[![Run Full Suite of Checks and Tests](https://github.com/magneticstain/plexer-cli/actions/workflows/run_full_test_suite.yml/badge.svg)](https://github.com/magneticstain/plexer-cli/actions/workflows/run_full_test_suite.yml)
[![Release](https://github.com/magneticstain/plexer-cli/actions/workflows/release.yml/badge.svg?event=push)](https://github.com/magneticstain/plexer-cli/actions/workflows/release.yml)

## Summary

Plexer is a CLI tool that makes it easy to organize your media for [Plex Media Server](https://www.plex.tv/). It renames media files and directories to match [the hierarchical naming that Plex requires](https://support.plex.tv/articles/naming-and-organizing-your-movie-media-files/).

## Features

### Support

Currently, Plexer only supports organizing movies and other individual video files.

### How It Works

Plexer expects the source directory to contain **one subdirectory per movie**. For each subdirectory, Plexer:

1. Infers the movie's name, release year, and edition (e.g. `Director's Cut`, `Extended Edition`) from the directory name using heuristics
1. Prompts you for any metadata it couldn't infer (see [`--prompt`](#prompt-behavior))
1. Renames the directory to the Plex format, e.g. `The.Black.Phone.2021.1080p.WEBRip.x265-RARBG` → `The Black Phone (2021)`
1. Renames each video file inside it to match, e.g. `Blade Runner (1982) {edition-Final Cut}.mkv`
1. **Deletes** any file in the directory that isn't a supported file type (samples, `.txt` files, images, etc.)

Files that are already in the correct format are left alone. Symlinks are skipped, and Plexer refuses to rename or delete anything outside of the source directory.

> [!WARNING]
> Plexer renames files and deletes unsupported files **in place, inside the source directory**. Run it with `--dry-run -vv` first to preview what it will do, and keep a backup of anything you can't replace.

### Roadmap

- [ ] Support for TV Shows ([#28](https://github.com/magneticstain/plexer-cli/issues/28))
- [X] Docker implementations ([#29](https://github.com/magneticstain/plexer-cli/issues/29))
- [ ] MacOS support ([#30](https://github.com/magneticstain/plexer-cli/issues/30))
- [ ] Windows support ([#31](https://github.com/magneticstain/plexer-cli/issues/31))
- [X] Metadata inference using file/directory info (i.e. analyze the video files to "guess" what the name, year, etc is) ([#32](https://github.com/magneticstain/plexer-cli/issues/32))

## Install

### Docker

The most portable way to install and run Plexer is by using Docker.

#### Via Container Registry

The easiest way to run Plexer in Docker is by using the public images hosted on container registries. Plexer images are available on both Docker Hub and GitHub Container Registry.

Mount your media directory into the container and pass Plexer's arguments after the image name. Without arguments, the container prints the help text. The container runs as a non-root user (UID/GID `1001`), so the mounted directory must be writable by that user.

##### Docker Hub

```bash
docker run --rm -it -v /path/to/media:/media magneticstain/plexer-cli \
  --source-dir /media --destination-dir /media --dry-run -vv
```

##### GitHub Container Registry

```bash
docker run --rm -it -v /path/to/media:/media ghcr.io/magneticstain/plexer-cli \
  --source-dir /media --destination-dir /media --dry-run -vv
```

#### Via Local Image Build

If the container registries are unavailable, you can also build the image locally. Clone this repo, build the Plexer image, and run it.

```bash
git clone https://github.com/magneticstain/plexer-cli.git
cd plexer-cli
docker build -t plexer_cli .
docker run --rm -it -v /path/to/media:/media plexer_cli \
  --source-dir /media --destination-dir /media --dry-run -vv
```

### PyPI

Plexer is published on [PyPI](https://pypi.org/project/plexer-cli/) and requires Python 3.10 or newer. Installing it with [pipx](https://pipx.pypa.io/) or [uv](https://docs.astral.sh/uv/) keeps it isolated from your other Python packages:

```bash
pipx install plexer-cli
# or
uv tool install plexer-cli
```

This installs the `plexer` command. Native installs also need libmagic; see [Requirements](#requirements) below.

## Requirements

### Linux and MacOS Native Install

If you've installed Plexer natively (i.e. outside of a Docker container) on Ubuntu, Debian, Fedora, etc., or MacOS, you will also need to install additional dependencies:

#### Python-Magic

Plexer uses `python-magic` to detect file types. It's installed automatically as a Python dependency, but it depends on the libmagic C library, which isn't. To install this library, follow [the installation instructions provided in the `python-magic` README](https://github.com/ahupp/python-magic?tab=readme-ov-file#installation). For example:

```bash
# Debian/Ubuntu
sudo apt-get install libmagic1

# MacOS (Homebrew)
brew install libmagic
```

The Docker image already includes libmagic.

## Usage

The source directory is the directory containing the raw media, with one subdirectory per movie.

```text
usage: plexer [-h] [-v] [--version] -s SOURCE_DIR -d DESTINATION_DIR
              [--prompt {all,none,default}] [--dry-run]

options:
  -h, --help            show this help message and exit
  -v, --verbose         Verbosity (-v, -vv, etc)
  --version             show program's version number and exit
  -s, --source-dir SOURCE_DIR
  -d, --destination-dir DESTINATION_DIR
  --prompt {all,none,default}
                        Behavior to take in regards to user prompts (e.g.
                        correcting names for overwriting files). all = prompt
                        user for every artifact; none = never prompt - just
                        trust the heuristics; default = prompt for incomplete
                        matches only
  --dry-run             Perform a trial run with no changes made
```

> [!NOTE]
> `--destination-dir` is required, but Plexer doesn't use it yet. All changes are currently made in place, inside the source directory.

### Example

```bash
# preview the changes first
plexer -s ~/Downloads/movies -d ~/Downloads/movies --dry-run -vv

# then apply them
plexer -s ~/Downloads/movies -d ~/Downloads/movies -v
```

### Prompt Behavior

The `--prompt` option controls when Plexer asks you to confirm or correct a movie's name, edition, and release year:

| Value     | Behavior                                                                                    |
| --------- | ------------------------------------------------------------------------------------------- |
| `default` | Prompt only when the name or release year can't be inferred from the directory name         |
| `all`     | Prompt for every movie directory, pre-filled with whatever was inferred                     |
| `none`    | Never prompt; directories whose metadata can't be inferred are skipped                      |

### Logging

By default, only warnings and errors are printed. Use `-v` for informational output and `-vv` for debug output, which shows each rename and delete operation.

### Supported File Types

Plexer keeps and renames the following file types; anything else inside a movie directory is deleted:

- MP4 video (`video/mp4`)
- Matroska video (`.mkv`, `video/x-matroska`)

File types are detected from file contents using libmagic, not from the file extension.

## Support & Feedback

If you run into issues while using Plexer, think you know a way to make it better, or just need help using it, [create a new issue](https://github.com/magneticstain/plexer-cli/issues/new/choose) and it will be triaged when possible. Additional documentation is available in the [project wiki](https://github.com/magneticstain/plexer-cli/wiki).

To report a security vulnerability, follow the process in [SECURITY.md](SECURITY.md) instead of opening a public issue.

## Development

### Software Stack

[![Hatch project](https://img.shields.io/badge/%F0%9F%A5%9A-Hatch-4051b5.svg)](https://github.com/pypa/hatch)
[![uv](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json)](https://github.com/astral-sh/uv)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

For developing with Plexer, there are several tools that are in use:

1. Build Backend and Packaging:
   1. [Hatch](https://hatch.pypa.io/)
1. Dependency Management:
   1. [uv](https://docs.astral.sh/uv/)
1. Analysis Tools:
   1. [Ruff](https://docs.astral.sh/ruff/)
   1. [actionlint](https://github.com/rhysd/actionlint)
1. Testing:
   1. [Pytest](https://docs.pytest.org/en/latest/)
   1. [Tox](https://tox.wiki/en/stable/)

Tool versions used for development are pinned in `.tool-versions` and `.python-version`.

### Getting Started

```bash
git clone https://github.com/magneticstain/plexer-cli.git
cd plexer-cli
uv sync
pre-commit install
```

You'll also need libmagic installed locally (see [Requirements](#requirements)).

### Coding Standards and Conventions

- Pre-commit hooks are utilized and managed in `.pre-commit-config.yaml`
  - For example, `ruff` is run as part of every commit
  - These pre-commit hooks **MUST** be installed and utilized by all developers
- See the [Code of Conduct](CODE_OF_CONDUCT.md) for community guidelines

#### Testing

- All functions **MUST** have unit tests created for them
- Unit tests live in `tests/` and can be run with `uv run pytest`, or across all supported Python versions along with formatting and linting checks using `tox`
- For manual end-to-end testing, `tests/bootstrap/bootstrap_plexer_e2e.sh` creates sample media in `/tmp/plexer-e2e`
  - Run it from the repo root, then use the launch configurations in `.vscode/launch.json` (or run `plexer` directly) against those directories
