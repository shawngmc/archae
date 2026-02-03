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
