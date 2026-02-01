"""Runtime config management (default, userconfig and envvars)."""

from pathlib import Path

import platformdirs
from dynaconf import Dynaconf

# Get the package directory for default settings
package_dir = Path(__file__).parent
default_settings_file = package_dir / "default_settings.toml"

# Get the config directory following XDG standards
config_dir = Path(platformdirs.user_config_dir("archae"))
config_dir.mkdir(parents=True, exist_ok=True)

# Define the user config file path
user_config_file = config_dir / "settings.toml"

# Create a default settings.toml if it doesn't exist
if not user_config_file.exists():
    user_config_file.write_text("""# Archae configuration
# Override defaults from the package here
""")

settings = Dynaconf(
    envvar_prefix="ARCHAE",
    settings_files=[
        str(default_settings_file),  # Load package defaults first
        str(user_config_file),  # User settings override defaults
    ],
    environments=True,
)

default_settings = Dynaconf(
    envvar_prefix="ARCHAE",
    settings_files=[
        str(default_settings_file),  # Load package defaults first
    ],
    environments=True,
)
