"""Runtime config management (default, userconfig and envvars)."""

import ast
import importlib
import typing
from pathlib import Path

import platformdirs
import yaml
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


options_file = package_dir / "options.yaml"


def get_options() -> dict:
    """Return the contents of options.yaml."""
    with Path.open(options_file) as f:
        return yaml.safe_load(f)


def get_converter(converter_def: str) -> typing.Callable:
    """Dynamically import and instantiate a converter class.

    Args:
        converter_def (str): Converter definition in format "module.path:ClassName" or a builtin type like "float" or "int".

    Returns:
        Converter function.
    """
    # Handle built-in types
    if converter_def == "float":
        return float
    if converter_def == "int":
        return int
    if converter_def == "bool":
        return ast.literal_eval

    # Split the definition into module path and class name
    module_name, class_name = converter_def.split(":")

    # Import the module
    module = importlib.import_module(module_name)

    # Get the class from the module
    return getattr(module, class_name)


def apply_options(option_list: dict[str, str | int | float | bool]) -> None:
    """Apply a dict of options to the current settings.

    Args:
        option_list (dict[str, str | int | float | bool]): Dictionary of options to apply.

    """
    options = get_options()
    for key, value in option_list.items():
        # Find the option definition by matching the key
        option_def = None
        for def_key in options:
            option_def = options[def_key]
            break
        if option_def:
            settings[key] = value
        else:
            pass


def convert_settings(settings_dict: dict) -> dict:
    """Convert settings using their defined converters.

    Args:
        settings_dict (dict): The settings dictionary to convert.

    Returns:
        dict: The converted settings dictionary.
    """
    options = get_options()
    for key in options:
        option_def = options[key]
        if "converter" in option_def and key in settings_dict:
            converter = get_converter(option_def["converter"])
            settings_dict[key] = converter(settings_dict[key])
    return settings_dict


def get_settings() -> dict:
    """Get the current settings after converting them.

    Returns:
        dict: The current settings as a dictionary.
    """
    return convert_settings(dict(settings))


def get_default_settings() -> dict:
    """Get the default settings after converting them.

    Returns:
        dict: The default settings as a dictionary.
    """
    return convert_settings(dict(default_settings))


def option_keys() -> list[str]:
    """Get a list of all available option keys.

    Returns:
        list[str]: List of option keys.
    """
    options = get_options()
    return list(options.keys())
