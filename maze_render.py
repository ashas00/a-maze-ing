"""Pure ASCII rendering of a Maze into lines of text (no curses/IO here)."""

from typing import List
from maze_model import Maze, EAST, NORTH, SOUTH, WEST


def render_lines(maze: Maze, show_path: bool) -> List[str]:
    """Render maze into a list of equal-length text rows."""
    rows = maze.height * 2 + 1
    cols = maze.width * 2 + 1
    grid = [
        ["█" if r % 2 == 0 and c % 2 == 0 else " " for c in range(cols)]
        for r in range(rows)
    ]

    for y in range(maze.height):
        for x in range(maze.width):
            walls = maze.grid[y][x]
            r, c = y * 2 + 1, x * 2 + 1
            if walls & NORTH:
                grid[r - 1][c] = "█"
            if walls & SOUTH:
                grid[r + 1][c] = "█"
            if walls & WEST:
                grid[r][c - 1] = "█"
            if walls & EAST:
                grid[r][c + 1] = "█"

    if show_path:
        for x, y in maze.path:
            grid[y * 2 + 1][x * 2 + 1] = "."

    ex, ey = maze.entry
    xx, xy = maze.exit
    grid[ey * 2 + 1][ex * 2 + 1] = "S"
    grid[xy * 2 + 1][xx * 2 + 1] = "E"

    return ["".join(row) for row in grid]
