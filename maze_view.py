"""Interactive curses viewer for a Maze: regenerate, toggle path, colors."""

import curses
from typing import Callable, List
from maze_model import Maze
from maze_render import render_lines


_COLORS = [
    curses.COLOR_WHITE, curses.COLOR_CYAN,
    curses.COLOR_YELLOW, curses.COLOR_GREEN,
]
_HELP = "r: regenerate  p: toggle path  c: color  q: quit"


def _draw(win: curses.window, lines: List[str], color_index: int) -> None:
    win.erase()
    pair = curses.color_pair(color_index + 1)
    try:
        for row, line in enumerate(lines):
            win.addstr(row, 0, line, pair)
        win.addstr(len(lines) + 1, 0, _HELP)
    except curses.error:
        pass
    win.refresh()


def _main(stdscr: curses.window, maze_factory: Callable[[], Maze]) -> None:
    curses.curs_set(0)
    curses.start_color()
    curses.use_default_colors()
    for index, color in enumerate(_COLORS, start=1):
        curses.init_pair(index, color, -1)

    maze = maze_factory()
    show_path = True
    color_index = 0

    while True:
        _draw(stdscr, render_lines(maze, show_path), color_index)
        key = stdscr.getch()
        if key in (ord("q"), 27):
            break
        elif key == ord("r"):
            maze = maze_factory()
        elif key == ord("p"):
            show_path = not show_path
        elif key == ord("c"):
            color_index = (color_index + 1) % len(_COLORS)


def run_viewer(maze_factory: Callable[[], Maze]) -> None:
    """Run the interactive viewer; maze_factory builds/regenerates a Maze."""
    curses.wrapper(_main, maze_factory)
