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

 Usage: archae [OPTIONS] INPUT

 Repeat the input.
 Archae explodes archives.

╭─ Arguments ──────────────────────────────────────────────────────────────────────────╮
│ *  INPUT_  INPUT  [required]                                                         │
╰──────────────────────────────────────────────────────────────────────────────────────╯
╭─ Options ────────────────────────────────────────────────────────────────────────────╮
│ --reverse  -r  Reverse the input.                                                    │
│ --version  -v  Show the version and exit.                                            │
│ --help     -h  Show this message and exit.                                           │
╰──────────────────────────────────────────────────────────────────────────────────────╯
```

<!-- [[[end]]] -->
