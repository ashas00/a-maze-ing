from typing import List, Tuple
from maze_model import Maze


_LETTER = {(0, -1): "N", (0, 1): "S", (1, 0): "E", (-1, 0): "W"}


def _path_to_letters(path: List[Tuple[int, int]]) -> str:
    """Turn a list of adjacent cells into an 'N'/'E'/'S'/'W' move string.

    Args:
        path: Ordered cells from entry to exit, empty if unreachable.

    Returns:
        str: One direction letter per step, empty for a path of 0 or 1 cell.
    """
    letters = []
    for (x1, y1), (x2, y2) in zip(path, path[1:]):
        letters.append(_LETTER[(x2 - x1, y2 - y1)])
    return "".join(letters)


def write_output(maze: Maze, output_file: str) -> None:
    """Write the wall grid, entry, exit and shortest path to output_file."""
    line = ["".join(format(cell, "X") for cell in row) for row in maze.grid]
    line.append("")
    line.append(f"{maze.entry[0]},{maze.entry[1]}")
    line.append(f"{maze.exit[0]},{maze.exit[1]}")
    line.append(_path_to_letters(maze.path))
    with open(output_file, "w",  encoding="utf-8") as out:
        out.write("\n".join(line) + "\n")
