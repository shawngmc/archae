"""File size conversion utilities."""

import re

from archae.util.enum.byte_scale import ByteScale


def compact_value(value: float) -> str:
    """Convert a float of file size to a FileSize string.

    Args:
        value (float): The size to convert

    Returns:
        str: A string with the most collapsed exact byte size rep.

    """
    exponent = 0
    modulo: float = 0
    while modulo == 0 and exponent < int(ByteScale.PETA.value):
        modulo = value % 1024
        if modulo == 0:
            exponent += 1
            value = int(value / 1024)
    return f"{value}{ByteScale(exponent).prefix_letter}"  # type: ignore[call-arg]


def expand_value(value: str | int) -> int:
    """Convert a FileSize string or int to an int.

    Args:
        value (str | int): The value to convert as necessary.

    Returns:
        int: Size in bytes

    """
    try:
        return int(value)
    except ValueError:
        pass
    except TypeError:
        pass

    # Regex to split number and unit
    match = re.match(r"^(\d+(?:\.\d+)?)\s*([KMGTP]B?)$", str(value), re.IGNORECASE)
    if not match:
        msg = f"{value} is not a valid file size (e.g., 10G, 500M)"
        raise ValueError(msg)

    number, unit = match.groups()
    number = float(number)
    unit = unit[0].upper()

    byte_scale = 1024 ** (ByteScale.from_prefix_letter(unit).value)

    # Default to bytes if no specific unit multiplier, or assume B
    return int(number * byte_scale)


def convert(value: str | int) -> int:
    """Convert a FileSizeParam to an int.

    Args:
        value (click.Option): The value to convert as necessary.
        param (str): The param we are validating.
        ctx (click.Context): The click Context to fail if we can't parse it.

    Returns:
        int: Size in bytes

    """
    try:
        return expand_value(value)
    except ValueError as err:
        msg = f"Could not convert {value} to file size: {err}"
        raise ValueError(msg) from err
