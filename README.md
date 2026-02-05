<!-- start docs-include-index -->

# Archae

![Archae Logo of a spider exploring a sarcophagus](./_static/archae_logo.png)

[![PyPI](https://img.shields.io/pypi/v/archae)](https://pypi.org/project/archae/)
[![Supported Python Versions](https://img.shields.io/pypi/pyversions/archae)](https://pypi.org/project/archae/)
[![pre-commit.ci status](https://results.pre-commit.ci/badge/github/shawngmc/archae/main.svg)](https://results.pre-commit.ci/latest/github/shawngmc/archae/main)
[![Test](https://github.com/shawngmc/archae/actions/workflows/test.yml/badge.svg)](https://github.com/shawngmc/archae/actions/workflows/test.yml)
[![Documentation Status](https://readthedocs.org/projects/archae/badge/?version=latest)](https://archae.readthedocs.io/en/latest/?badge=latest)
[![PyPI - License](https://img.shields.io/pypi/l/archae)](https://img.shields.io/pypi/l/archae)

Archae explodes archives.

<!-- end docs-include-index -->

## Why

Every once and a while, I run into an issue: multiple layers of archives. The reasons vary, but examples would include:

- Searching for something in a ZIP of folders that contained a ZIP with a CD image in it
- Running a malware scan and finding an obscure archive format was missed and not even flagged.
- Meanwhile, I want to make sure I don't fill my disk, especially if an archive bomb (more commonly known as a ZIP bomb) has been jammed in somewhere. They're only funny the first time. :D

## Features

- Uses 7z/unar to try to extract archives
- No substantial limit on the number of archive layers
- Identifies file types via libmagic
- Detects duplicate archives
- Can detect password-protected archives and extract any unprotected entries
- Basic archive bomb protections
    - MAX_ARCHIVE_SIZE_BYTES - ensures the uncompressed size of an archive is limited
    - MAX_TOTAL_SIZE_BYTES - ensures the total extracted footprint isn't above a certain size
    - MIN_ARCHIVE_RATIO - ensures very-high-compression-ratio archives are stopped
    - MIN_DISK_FREE_SPACE - minimum free space at the extraction location
    - MAX_DEPTH - allow setting a maximum archive depth to traverse
    - DELETE_ARCHIVES_AFTER_EXTRACTION - delete pure archive types after deletion

## Installation

<!-- start docs-include-installation -->

Archae is available on [PyPI](https://pypi.org/project/archae/). Install with [uv](https://docs.astral.sh/uv/) or your package manager of choice:

```sh
uv tool install archae
```

<!-- end docs-include-installation -->

## Documentation

Check out the [Archae documentation](https://archae.readthedocs.io/en/stable/) for the [User's Guide](https://archae.readthedocs.io/en/stable/usage.html) and [CLI Reference](https://archae.readthedocs.io/en/stable/cli.html).

## Usage

Configuration values are supplied one of four ways, and any item lower in this list will overwrite a prior one:

- Default values are stored in the app
- A TOML file at ~/.config/archae/ will be created on first run and can override those values (ex. MIN_ARCHIVE_RATIO = 0.005)
- Env vars starts starting with "ARCHAE\_" are parsed (ex. ARCHAE_MIN_ARCHIVE_RATIO=0.005)
- Values can be passed in as flags (ex. --min_archive_ratio=0.005)

<!-- start docs-include-usage -->

Running `archae --help` or `python -m archae --help` shows a list of all of the available options and arguments:

<!-- [[[cog
import cog
from archae import cli
from click.testing import CliRunner
runner = CliRunner()
result = runner.invoke(cli.cli, ["--help"], terminal_width=88)
help = result.output.replace("Usage: cli", "Usage: archae")
cog.outl(f"\n```sh\narchae --help\n{help.rstrip()}\n```\n")
]]] -->

```sh
archae --help

 Usage: archae [OPTIONS] COMMAND [ARGS]...

 Archae explodes archives.

╭─ Options ────────────────────────────────────────────────────────────────────────────╮
│ --version  -v  Show the version and exit.                                            │
│ --help     -h  Show this message and exit.                                           │
╰──────────────────────────────────────────────────────────────────────────────────────╯
╭─ Commands ───────────────────────────────────────────────────────────────────────────╮
│ extract         Extract and analyze an archive.                                      │
│ listopts        List all available configuration options.                            │
│ status          Show archae status and available tools.                              │
╰──────────────────────────────────────────────────────────────────────────────────────╯
```

<!-- [[[end]]] -->

<!-- end docs-include-usage -->
