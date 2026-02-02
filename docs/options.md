# Configuration Options

Archae has several configuration options that control its behavior. These can be set via environment variables, configuration files, or programmatically through the library.

## Order of precedence

- Default values
- User config file (~/.config/archae)
- Env vars
- Invoker (CLI: -o flags / Module: the apply_options function)

## Options

<!-- [[[cog
import cog
import yaml
from pathlib import Path

# Load the options from the options.yaml file
options_path = Path(__file__).parent.parent / "src" / "archae" / "options.yaml"
with open(options_path) as f:
    options = yaml.safe_load(f)

# Load the default settings
defaults_path = Path(__file__).parent.parent / "src" / "archae" / "default_settings.toml"
defaults_content = defaults_path.read_text()
# Parse the [default] section
defaults = {}
in_default_section = False
for line in defaults_content.split('\n'):
    if line.strip() == '[default]':
        in_default_section = True
        continue
    if in_default_section and line.startswith('['):
        break
    if in_default_section and '=' in line:
        key, value = line.split('=', 1)
        defaults[key.strip()] = value.strip().strip('"')

# Generate the options documentation
for option_name in sorted(options.keys()):
    option_def = options[option_name]
    cog.outl(f"\n### {option_name}\n")
    cog.outl(f"**Type:** {option_def.get('type', 'unknown')}\n")
    cog.outl(f"**Description:** {option_def.get('help', 'No description available')}\n")
    if option_name in defaults:
        cog.outl(f"**Default:** `{defaults[option_name]}`\n")
    if "converter" in option_def:
        cog.outl(f"**Converter:** {option_def['converter']}\n")
    if "examples" in option_def:
        cog.outl("**Examples:**\n")
        for example in option_def["examples"]:
            cog.outl(f"- `{example}`\n")
]]] -->

## MAX_ARCHIVE_SIZE_BYTES

**Type:** int

**Description:** Maximum size of a single archive to extract in bytes.

**Default:** `10G`

**Converter:** archae.util.converter.file_size:convert

**Examples:**

- `1GB`
- `500M`
- `500`

## MAX_TOTAL_SIZE_BYTES

**Type:** int

**Description:** Maximum total size of all archives to extract in bytes.

**Default:** `100G`

**Converter:** archae.util.converter.file_size:convert

**Examples:**

- `1GB`
- `500M`
- `500`

## MIN_ARCHIVE_RATIO

**Type:** float

**Description:** Minimum compression ratio (compressed size / uncompressed size) required to extract an archive.

**Default:** `0.005`

**Examples:**

- `0.001`

## MIN_DISK_FREE_SPACE

**Type:** int

**Description:** Minimum required estimated disk space after extraction in bytes.

**Default:** `10G`

**Converter:** archae.util.converter.file_size:convert

**Examples:**

- `1GB`
- `500M`
- `500`

<!-- [[[end]]] -->

## Setting Configuration Options

### Via Environment Variables

Set environment variables prefixed with `ARCHAE_`:

```bash
export ARCHAE_MAX_ARCHIVE_SIZE_BYTES=5000000000
export ARCHAE_MIN_ARCHIVE_RATIO=0.01
```

### Via Configuration File

Edit `~/.config/archae/settings.toml`:

```toml
MAX_ARCHIVE_SIZE_BYTES = 5000000000
MIN_ARCHIVE_RATIO = 0.01
MIN_DISK_FREE_SPACE = 1000000000
```

### Via CLI Arguments

Pass options directly to the command line:

```bash
archae --max_archive_size_bytes=5000000000 --min_archive_ratio=0.01 archive.zip
```

### Programmatically

When using Archae as a library, use the `apply_settings()` method:

```python
from archae import ArchiveExtractor

extractor = ArchiveExtractor()
extractor.apply_settings([
    ("MAX_ARCHIVE_SIZE_BYTES", "5000000000"),
    ("MIN_ARCHIVE_RATIO", "0.01")
])
extractor.handle_file(Path("archive.zip"))
```
