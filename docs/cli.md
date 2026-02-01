# CLI Reference

This page lists the `--help` for `archae`.

## archae

Running `archae --help` or `python -m archae --help` shows a list of all of the available options and arguments:

<!-- [[[cog
import cog
from archae import cli
from click.testing import CliRunner
result = CliRunner().invoke(cli.cli, ["--help"], terminal_width=88)
help = result.output.replace("Usage: cli", "Usage: archae")
cog.outl(f"\n```sh\narchae --help\n{help.rstrip()}\n```\n")
]]] -->

```sh
archae --help

 Usage: archae [OPTIONS] ARCHIVE_PATH

 Archae explodes archives.

╭─ Arguments ──────────────────────────────────────────────────────────────────────────╮
│ *  ARCHIVE_PATH  FILE  Archive to examine [required]                                 │
╰──────────────────────────────────────────────────────────────────────────────────────╯
╭─ Options ────────────────────────────────────────────────────────────────────────────╮
│ --max_total_size_bytes        FILESIZE               Maximum total extraction size   │
│                                                      before failing, default 100G    │
│                                                      [default: 107374182400]         │
│ --max_archive_size_bytes      FILESIZE               Maximum individual archive      │
│                                                      extraction size before failing, │
│                                                      default 10G [default:           │
│                                                      10737418240]                    │
│ --min_archive_ratio           FLOAT RANGE [0<=x<=1]  Minimum allowed compression     │
│                                                      ratio for an archive. A         │
│                                                      floating-point value between    │
│                                                      0.0 and 1.0, inclusive. Default │
│                                                      is 0.005 [default: 0.005]       │
│ --version                 -v                         Show the version and exit.      │
│ --help                    -h                         Show this message and exit.     │
╰──────────────────────────────────────────────────────────────────────────────────────╯
```

<!-- [[[end]]] -->
