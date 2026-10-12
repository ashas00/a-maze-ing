<i>This project has been created as part of the 42 curriculum by olprymas, aperpetu.</i>

# A-Maze-ing

## Description

A-Maze-ing is a maze generator written in Python. Given a small configuration
file, it builds either a **perfect maze** (a single, unique path between the
entry and the exit, no loops) or a **playable board** (fully connected, with
open corners and centre, multiple independent routes, and a visible "42"
pattern drawn by isolated cells) — usable directly as a Pac-Man-like level.
The generated maze is written to a text file using a compact hexadecimal wall
encoding, and displayed interactively in the terminal.

## Instructions

Requires Python 3.10+.

```bash
make install   # create .venv and install dev dependencies (flake8, mypy)
make run       # run the maze generator with the default config.txt
make debug     # same, but through Python's pdb debugger
make lint      # flake8 + mypy
make lint-strict  # flake8 + mypy --strict
make clean     # remove __pycache__ / .mypy_cache
make fclean    # clean + remove .venv
```

Or run it directly:
```bash
python3 a_maze_ing.py config.txt
```
`config.txt` is the only argument — a plain text configuration file (see
below). Any config filename may be used.

Once running, the maze is written to `OUTPUT_FILE` and shown in an
interactive terminal viewer:

| Key | Action |
|---|---|
| `r` | Regenerate a new maze |
| `p` | Show / hide the shortest path |
| `c` | Cycle wall colours |
| `q` / `Esc` | Quit |

## Configuration File Format

One `KEY=VALUE` pair per line. Lines starting with `#` are comments and are
ignored.

| Key | Description | Example |
|---|---|---|
| `WIDTH` | Maze width, in cells | `WIDTH=20` |
| `HEIGHT` | Maze height, in cells | `HEIGHT=15` |
| `ENTRY` | Entry coordinates `x,y` (must be on the border) | `ENTRY=0,0` |
| `EXIT` | Exit coordinates `x,y` (must be on the border) | `EXIT=19,14` |
| `OUTPUT_FILE` | Where the generated maze is written | `OUTPUT_FILE=maze.txt` |
| `PERFECT` | `True` for a perfect (single-path) maze, `False` for a playable board | `PERFECT=True` |
| `SEED` | Optional. Fixes the random seed for reproducible generation | `SEED=42` |

A default `config.txt` is provided at the repository root.

## Maze Generation Algorithm

The maze is carved with an **iterative recursive backtracker**: starting
from the entry cell, it repeatedly moves to a random unvisited neighbour,
knocking down the wall between the two cells, and backtracks along a stack
once a cell has no unvisited neighbour left. This produces a spanning tree
over the grid — by construction, every cell is reachable and there are no
loops, which is exactly a perfect maze (`PERFECT=True`).

For the playable board (`PERFECT=False`), the same backtracker is reused,
with four extra passes:
- the cells forming the "42" pattern are marked as pre-visited *before* the
  backtracker runs, so it naturally routes around them instead of carving
  through them (they stay fully closed, matching the subject's isolated-cell
  exception);
- extra walls are randomly removed between neighbouring inner cells to
  introduce loops, giving the required multiple independent routes;
- the four corners are forced open toward the maze interior, keeping the
  outer border otherwise closed;
- any cell left with only one opening (a real dead-end) is given one more,
  towards a valid neighbour, until at most two dead-ends remain — the
  subject's tolerated minimum — instead of leaving it to chance.

The shortest path from entry to exit (used for the on-screen path and the
output file) is computed separately with a **breadth-first search (BFS)**
over the open passages — the natural choice for the shortest path on an
unweighted grid graph.

**Why this algorithm**: the recursive backtracker is simple to reason about,
guarantees full connectivity by construction (no separate connectivity
check is needed), and tends to produce long, winding corridors rather than
short, uniform ones — visually closer to a "real" maze than simpler
algorithms like randomized Prim's. Extending it with a small post-processing
pass to add loops let us reuse the exact same core algorithm for both modes,
instead of maintaining two separate generators.

## Reusable Code

The generator (`MazeGenerator`) lives in its own standalone module,
`maze_generator/`, with no dependency on any other file in this project —
it can be dropped into a future project as-is, or packaged and installed
with `pip` (built as `mazegen-*.whl` / `.tar.gz` from `pyproject.toml`).

```python
from maze_generator import MazeGenerator

generator = MazeGenerator(width=20, height=15)
generator.generate_grid(entry_x=0, entry_y=0, seed=42, perfect=False)

grid = generator.get_grid()  # List[List[int]], one wall bitmask per cell
path = generator.path_finder_bfs((0, 0), (19, 14))
```

`grid[y][x]` is a bitmask of the closed walls for that cell
(`MazeGenerator.NORTH | EAST | SOUTH | WEST` = 1, 2, 4, 8 — a set bit means
that wall is closed). `path_finder_bfs` returns the shortest path from entry
to exit as a list of `(x, y)` cells, or an empty list if unreachable. It has
no dependencies beyond the Python standard library.

## Team & Project Management

- **aperpetu** — maze generation algorithm (`MazeGenerator`): the recursive
  backtracker, the playable-mode passes (loops, open corners, "42" pattern),
  and the BFS shortest-path finder.
- **olprymas** — configuration parser, the interactive terminal (curses)
  viewer, the output file writer, packaging (`mazegen`), the Makefile, and
  integrating all the pieces together in `a_maze_ing.py`.

The project was split from the start along this generator / everything-else
line, using a shared, agreed-upon data contract (`Maze`: width, height, wall
grid, entry, exit, path) so both halves could be built and tested in
parallel — the viewer and output writer were developed and tested against a
throwaway placeholder generator while the real algorithm was still in
progress, then swapped in once it was ready. The provided `maze_analyzer.py`
was used throughout to catch real bugs early (wall-encoding mismatches
between neighbouring cells, cells left unreachable) rather than only at the
end.

**What worked well**: agreeing on the data contract early meant the two
halves of the project rarely blocked each other, and integration was a
small, predictable change each time rather than a rewrite. Running the
provided `maze_analyzer.py` against every generated maze during development
caught real, concrete bugs (mismatched wall encoding between neighbouring
cells, cells left unreachable) that would have been much harder to spot by
eye.
**What could be improved**: a couple of interface mismatches (argument
order, self/static method, return types) between the generator and the rest
of the code only surfaced when actually wiring things together — agreeing
on exact function signatures (not just the data shapes) earlier would have
avoided a round of back-and-forth fixes. The first version of the
loop-punching pass also only reduced the playable board's dead-end count
probabilistically, which was not reliable enough to consistently meet the
subject's limit — replacing it with a dedicated pass that deterministically
closes off dead-ends (rather than hoping random loops happen to remove
them) fixed it for good.

**Tools used**: git for collaboration, `flake8`/`mypy` for linting and type
checking, and AI assistant to help write README file

## Resources

- [Maze generation algorithm — Wikipedia](https://en.wikipedia.org/wiki/Maze_generation_algorithm)
- [Recursive backtracker maze algorithm (Jamis Buck)](https://weblog.jamisbuck.org/2010/12/27/maze-generation-recursive-backtracking)
- [Breadth-first search — Wikipedia](https://en.wikipedia.org/wiki/Breadth-first_search)
- [Python `curses` module documentation](https://docs.python.org/3/library/curses.html)

### AI
#### Gemini Pro 
- used for detailed explanations of different alogrithms
- used for debugging of code

#### Claude Opus 5
- used for the explanation of new concepts
- used for debugging of code