# Using Archae as a Python Library

While Archae is primarily designed as a command-line tool, it can also be used as a Python library to programmatically extract and analyze archives in your own code.

## Installation

To use Archae as a library, install it with pip or your preferred package manager:

```bash
uv pip install archae
```

## Basic Usage

The main entry point for library usage is the `ArchiveExtractor` class from `archae.extractor`.

### Simple Example

```python
from pathlib import Path
from archae.extractor import ArchiveExtractor

# Create an extractor instance
extractor = ArchiveExtractor(base_dir=Path("."))

# Process an archive
archive_path = Path("my_archive.zip")
extractor.handle_file(archive_path)

# Retrieve extracted files information
tracked_files = extractor.get_tracked_files()
for file_hash, file_info in tracked_files.items():
    print(f"Hash: {file_hash}")
    print(f"Info: {file_info}")
```

## Core Classes and Methods

### ArchiveExtractor

The main class for handling archive extraction and file tracking.

#### Constructor

```python
ArchiveExtractor(base_dir: Path | None = None)
```

**Parameters:**

- `base_dir` (optional): The base directory for extraction operations. Defaults to the current working directory. An `extracted/` subdirectory will be created here to store extracted files.

#### Key Methods

##### `handle_file(file_path: Path)`

Process a file or archive. Recursively extracts archives and tracks all files.

**Parameters:**

- `file_path`: Path to the file or archive to process

**Example:**

```python
extractor.handle_file(Path("archive.tar.gz"))
```

##### `get_tracked_files() -> dict[str, dict]`

Retrieve information about all tracked files.

**Returns:** Dictionary mapping file hashes to their metadata including:

- `size`: File size in bytes
- `type`: File type (from libmagic)
- `type_mime`: MIME type
- `extension`: File extension
- `is_archive`: Whether the file is an archive
- `extracted_size`: Uncompressed size (for archives)
- `overall_compression_ratio`: Compression ratio (for archives)

**Example:**

```python
files = extractor.get_tracked_files()
for file_hash, metadata in files.items():
    print(f"{file_hash}: {metadata['size']} bytes")
```

##### `get_warnings() -> list[str]`

Retrieve accumulated warnings from the extraction process.

**Returns:** List of warning messages

**Example:**

```python
warnings = extractor.get_warnings()
for warning in warnings:
    print(f"Warning: {warning}")
```

##### `get_default_settings() -> dict`

Get the default settings from the config module.

**Returns:** Dictionary of default settings

**Example:**

```python
defaults = extractor.get_default_settings()
print(f"Default max archive size: {defaults['MAX_ARCHIVE_SIZE_BYTES']}")
```

##### `apply_settings(option_list: list[tuple[str, str]])`

Apply a list of settings options as (key, value) tuples.

**Parameters:**

- `option_list`: List of (key, value) tuples to apply

**Example:**

```python
extractor.apply_settings([
    ("MAX_ARCHIVE_SIZE_BYTES", "5000000000"),
    ("MIN_ARCHIVE_RATIO", "0.01")
])
```

## Configuration

Archae's behavior can be configured via the settings system. The same configuration options available in the CLI are accessible when using the library:

```python
from archae.config import settings

# View current settings
print(settings["MAX_ARCHIVE_SIZE_BYTES"])
print(settings["MAX_TOTAL_SIZE_BYTES"])
print(settings["MIN_ARCHIVE_RATIO"])
print(settings["MIN_DISK_FREE_SPACE"])
```

For details on these settings and how to configure them, see the [CLI Reference](cli.md).

## Advanced Examples

### Processing Multiple Archives

```python
from pathlib import Path
from archae.extractor import ArchiveExtractor

extractor = ArchiveExtractor(base_dir=Path("./output"))

archives = Path(".").glob("*.zip")
for archive in archives:
    print(f"Processing {archive}")
    try:
        extractor.handle_file(archive)
    except Exception as e:
        print(f"Error processing {archive}: {e}")

# Get results
tracked = extractor.get_tracked_files()
print(f"Total files tracked: {len(tracked)}")
```

### Analyzing Extraction Results

```python
from archae.extractor import ArchiveExtractor
from pathlib import Path

extractor = ArchiveExtractor()
extractor.handle_file(Path("complex_archive.tar.gz"))

tracked = extractor.get_tracked_files()

# Find all archives
archives = [
    (hash_, meta)
    for hash_, meta in tracked.items()
    if meta.get("is_archive")
]

print(f"Found {len(archives)} nested archives")

# Find files with high compression ratio (potential bombs)
for file_hash, metadata in tracked.items():
    if metadata.get("is_archive"):
        ratio = metadata.get("overall_compression_ratio", 0)
        if ratio > 100:  # 100x compression
            print(f"Highly compressed archive: {file_hash}")
```

### Getting File Statistics

```python
from archae.extractor import ArchiveExtractor
from pathlib import Path

extractor = ArchiveExtractor()
extractor.handle_file(Path("archive.zip"))

tracked = extractor.get_tracked_files()

# Calculate total extracted size
total_size = sum(f.get("size", 0) for f in tracked.values())
print(f"Total extracted size: {total_size} bytes")

# Count files by type
types = {}
for metadata in tracked.values():
    file_type = metadata.get("type", "unknown")
    types[file_type] = types.get(file_type, 0) + 1

for file_type, count in sorted(types.items(), key=lambda x: x[1], reverse=True):
    print(f"{file_type}: {count} files")
```

## Error Handling

The extractor includes built-in protections against archive bombs and other issues. Check warnings after processing:

```python
from archae.extractor import ArchiveExtractor
from pathlib import Path

extractor = ArchiveExtractor()
extractor.handle_file(Path("suspicious.zip"))

# Get any warnings about skipped archives
warnings = extractor.get_warnings()
if warnings:
    print("Processing completed with warnings:")
    for warning in warnings:
        print(f"  - {warning}")
```

## Notes

- Archives are automatically detected based on file MIME type and extension
- The extractor uses libmagic for accurate file type detection
- By default, an `extracted/` directory is created in the base directory
- The extractor is not thread-safe and should be used with one file at a time
- Warnings are accumulated during processing and can be retrieved after completion
