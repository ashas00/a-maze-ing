"""Parser for the A-Maze-ing maze generator's configuration file"""

from dataclasses import dataclass
from typing import Dict, Optional, Tuple


class ConfigError(Exception):
    """Raised when a configuration file is missing, malformed or invalid"""


@dataclass
class MazeConfig:
    """Validated maze generation options read from a configuration file"""

    width: int
    height: int
    entry: Tuple[int, int]
    exit: Tuple[int, int]
    output_file: str
    perfect: bool
    seed: Optional[int] = None


MANDATORY_KEYS = ("WIDTH", "HEIGHT", "ENTRY", "EXIT", "OUTPUT_FILE", "PERFECT")


def _pair(value: str) -> Tuple[int, int]:
    """Parse an "x,y" string into an (x, y) coordinate tuple"""
    x, y = value.split(",")
    return int(x), int(y)


def _on_border(cell: Tuple[int, int], width: int, height: int) -> bool:
    """True if cell lies on the outer edge of a width x height grid"""
    x, y = cell
    return x in (0, width - 1) or y in (0, height - 1)


def parse_config(path: str) -> MazeConfig:
    """Parse and validate a maze configuration file into a MazeConfig"""
    try:
        with open(path, encoding="utf-8") as config_file:
            lines = config_file.readlines()
    except OSError as exc:
        raise ConfigError(f"cannot open '{path}': {exc}") from exc

    pairs: Dict[str, str] = {}
    for line_number, line in enumerate(lines, start=1):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            raise ConfigError(f"{path}:{line_number}: invalid "
                              f"syntax, expected KEY=VALUE")
        key, value = line.split("=", 1)
        pairs[key.strip().upper()] = value.strip()

    missing = [key for key in MANDATORY_KEYS if key not in pairs]
    if missing:
        raise ConfigError(f"missing mandatory key(s): {', '.join(missing)}")

    try:
        width = int(pairs["WIDTH"])
        height = int(pairs["HEIGHT"])
        entry = _pair(pairs["ENTRY"])
        exit_ = _pair(pairs["EXIT"])
        seed = int(pairs["SEED"]) if "SEED" in pairs else None
    except ValueError as exc:
        raise ConfigError(f"invalid value in config: {exc}") from exc

    perfect_raw = pairs["PERFECT"].strip().lower()
    if perfect_raw not in ("true", "false"):
        raise ConfigError(
            f"PERFECT: expected True or False, got '{pairs['PERFECT']}'"
        )
    perfect = perfect_raw == "true"

    output_file = pairs["OUTPUT_FILE"].strip()
    if not output_file:
        raise ConfigError("OUTPUT_FILE: must not be empty")
    if width <= 0 or height <= 0:
        raise ConfigError("WIDTH and HEIGHT must be positive")
    if not (0 <= entry[0] < width and 0 <= entry[1] < height):
        raise ConfigError(f"ENTRY {entry} is outside the {width}x{height}")
    if not (0 <= exit_[0] < width and 0 <= exit_[1] < height):
        raise ConfigError(f"EXIT {exit_} is outside the {width}x{height}")
    if entry == exit_:
        raise ConfigError("ENTRY and EXIT must be different cells")
    if not _on_border(entry, width, height):
        raise ConfigError(f"ENTRY {entry} must be on the maze border")
    if not _on_border(exit_, width, height):
        raise ConfigError(f"EXIT {exit_} must be on the maze border")

    return MazeConfig(width, height, entry, exit_, output_file, perfect, seed)
