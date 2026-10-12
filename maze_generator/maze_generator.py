import random
from typing import List, Set, Tuple, Dict
from collections import deque
from sys import stderr


class MazeGenerator():
    """Generate and solve grid-based mazes. Standard library only.

    Size is set on the constructor, everything else on ``generate_grid``,
    which may be called again to recarve the same grid::

        from maze_generator import MazeGenerator

        gen = MazeGenerator(20, 15)          # width, height, 1 or more
        gen.generate_grid(0, 0, seed=42, perfect=False)

        grid = gen.get_grid()                          # the structure
        path = gen.path_finder_bfs((0, 0), (19, 14))   # the solution

    ``generate_grid(entry_x, entry_y, seed, perfect=False)``
        ``entry_x, entry_y`` is the cell the carving starts from: inside
        the grid, outside the "42". ``seed`` fixes every random choice, so
        the same size, entry, seed and mode rebuild an identical maze.
        ``perfect=True`` gives exactly one route between any two cells,
        ``False`` a braided Pac-Man board -- several independent routes,
        open corners, no dead-ends.

    Access generated structure: ``get_grid() -> List[List[int]]``
        A fresh copy of the walls, indexed **row first**: ``grid[y][x]``.
        Each cell is four bits, a *set* bit meaning that wall is *closed*
        (NORTH 1, EAST 2, SOUTH 4, WEST 8), so 15 is sealed, 0 is open::

            bool(grid[0][0] & MazeGenerator.EAST)   # False -> open

    Acces at least one solution: ``path_finder_bfs(entry, exit_) -> List[Tuple
        [int, int]]`` Shortest route between two ``(x, y)`` cells, entry and
        exit included: ``[(0, 0), (1, 0), (2, 0), ...]``, so ``len(path) - 1``
        steps. Empty when the exit is unreachable or a coordinate is out of
        bounds. These are cells, not moves -- an ``'N'/'E'/'S'/'W'`` string
        is the caller's to derive.

    ``pattern -> Set[Tuple[int, int]]``
        The sealed ``(x, y)`` cells drawing the "42", the only ones a
        caller should ever find unreachable. Empty below 14x10.

    Raises:
        ValueError: A dimension below 1, or an entry out of bounds or
            inside the "42".
    """
    NORTH: int = 1
    EAST: int = 2
    SOUTH: int = 4
    WEST: int = 8

    DIRECTIONS: Tuple[Tuple[int, int, int, int], ...] = (
            (0, -1, NORTH, SOUTH),
            (1, 0, EAST, WEST),
            (0, 1, SOUTH, NORTH),
            (-1, 0, WEST, EAST)
    )

    pattern_error_found = False

    def __init__(self, width: int, height: int) -> None:
        """
        Initialize maze grid with the specified dimensions from config file.

        Every cell gets filled with num 15 (binary 1111), starting the maze as
        a block of closed cells with no open paths yet.

        Args:
            width (int): horizontal cells
            height (int): vertical cells
        """
        if width < 1 or height < 1:
            raise ValueError(f"Maze size {width}x{height} is invalid, width"
                             f" and height must be at least 1.")
        self.width = width
        self.height = height
        self.grid: List[List[int]] = [[15 for _ in range(width)] for _ in
                                      range(height)]
        self.pattern: Set[Tuple[int, int]] = self._create_42_pattern()

    def _reset_grid(self) -> None:
        """Close every wall again so a new maze can be carved from scratch."""
        self.grid = [[15 for _ in range(self.width)] for _ in
                     range(self.height)]

    def _perfect_maze(self, entry_x: int, entry_y: int, seed: int) -> None:
        """Generate a perfect maze using the Recursive Backtracker algorithm.

        Args:
            entry_x (int): X-coordinate of the entry point.
            entry_y (int): Y-coordinate of the entry point.
            seed (int): Random seed for reproducible generation.
        """
        self._reset_grid()

        rnd = random.Random(seed)
        current_path: List[Tuple[int, int]] = [(entry_x, entry_y)]
        visited: Set[Tuple[int, int]] = {(entry_x, entry_y)}

        visited.update(self.pattern)

        while current_path:
            cx, cy = current_path[-1]
            not_visited = []

            for dx, dy, wall, other_wall in self.DIRECTIONS:
                nx, ny = cx + dx, cy + dy

                if 0 <= nx < self.width and 0 <= ny < self.height:
                    if (nx, ny) not in visited:
                        not_visited.append((nx, ny, wall, other_wall))

            if not_visited:
                nx, ny, wall, other_wall = rnd.choice(not_visited)

                self.grid[cy][cx] &= ~wall
                self.grid[ny][nx] &= ~other_wall

                visited.add((nx, ny))
                current_path.append((nx, ny))
            else:
                current_path.pop()

    def _create_42_pattern(self) -> Set[Tuple[int, int]]:
        """Create and return coordinates for the 42 pattern within the maze.

        Returns:
            Set[Tuple[int, int]]: Set of coordinate tuples forming the pattern.
        """
        min_w = 14
        min_h = 10

        if self.width < min_w or self.height < min_h:
            if not MazeGenerator.pattern_error_found:
                print("Error: Maze dimensions are too small, 42-pattern can't"
                      " be printed", file=stderr)
                MazeGenerator.pattern_error_found = True

            return set()

        start_x = (self.width // 2) - 3
        start_y = (self.height // 2) - 2

        pattern_cells = [
            (0, 0), (0, 1), (0, 2), (1, 2), (2, 0), (2, 1), (2, 2),
            (2, 3), (2, 4),
            (4, 0), (5, 0), (6, 0), (6, 1), (4, 2), (5, 2), (6, 2),
            (4, 3), (4, 4), (5, 4), (6, 4)
        ]

        return {(start_x + px, start_y + py) for px, py in pattern_cells
                if 0 <= start_x + px < self.width and 0 <= start_y + py
                < self.height}

    def create_playable_maze(self, entry_x: int, entry_y: int, seed:
                             int) -> None:
        """Create a playable maze by modifying a perfect maze layout.

        Args:
            entry_x (int): X-coordinate of the entry point.
            entry_y (int): Y-coordinate of the entry point.
            seed (int): Random seed for procedural adjustments.
        """
        self._perfect_maze(entry_x, entry_y, seed)
        self._outer_spaces_playable()
        self._inner_spaces_playable(seed)
        self._dead_ends_out(seed + 2)

    def _inner_spaces_playable(self, seed: int) -> None:
        """Open up random inner walls to create a more playable maze design.

        Args:
            seed (int): Random seed for wall removal choices.
        """
        rnd = random.Random(seed + 1)
        h = self.height - 1
        w = self.width - 1

        for y in range(1, h):
            for x in range(1, w):
                if (x, y) in self.pattern:
                    continue

                if rnd.choice([True, False]):
                    if (x + 1, y) not in self.pattern:
                        self._try_open_wall(x, y, x + 1, y, self.EAST,
                                            self.WEST)
                else:
                    if (x, y + 1) not in self.pattern:
                        self._try_open_wall(x, y, x, y + 1, self.SOUTH,
                                            self.NORTH)

    def _try_open_wall(self, x: int, y: int, nx: int, ny: int, wall: int,
                       opp_wall: int) -> bool:
        """Open the wall between two adjacent cells, unless doing so would
        create a fully open 3x3 area (no isolated cells left to explore).

        Args:
            x, y (int): Coordinates of the first cell.
            nx, ny (int): Coordinates of the adjacent cell.
            wall (int): Wall bit to clear on the first cell.
            opp_wall (int): Matching wall bit to clear on the adjacent cell.

        Returns:
            bool: True if the wall was opened, False if it was reverted.
        """
        old_cell = self.grid[y][x]
        old_neighbour = self.grid[ny][nx]

        self.grid[y][x] &= ~wall
        self.grid[ny][nx] &= ~opp_wall

        if self._creates_3x3_open_area(x, y, nx, ny):
            self.grid[y][x] = old_cell
            self.grid[ny][nx] = old_neighbour
            return False
        return True

    def _creates_3x3_open_area(self, x: int, y: int, nx: int,
                               ny: int) -> bool:
        """Check whether the two cells that were just modified belong to a
        3x3 block of cells with every wall between them open.

        Only the blocks containing those two cells can have become fully
        open, so the whole grid does not need to be scanned.

        Args:
            x, y (int): Coordinates of the first modified cell.
            nx, ny (int): Coordinates of the second modified cell.

        Returns:
            bool: True if such a block exists.
        """
        top_lcx = self.width - 3
        top_lcy = self.height - 3

        for cx, cy in ((x, y), (nx, ny)):
            for corner_y in range(cy - 2, cy + 1):
                for corner_x in range(cx - 2, cx + 1):
                    if 0 <= corner_x <= top_lcx and 0 <= corner_y <= top_lcy:
                        if self._block_fully_open(corner_x, corner_y):
                            return True
        return False

    def _block_fully_open(self, top_lcx: int, top_lcy: int) -> bool:
        """Check whether the 3x3 block with top-left cell (top_lcx, top_lcy)
        has every internal wall between its cells open.

        Args:
            ox, oy (int): Top-left coordinates of the 3x3 block.

        Returns:
            bool: True if the block is fully open internally.
        """
        for dy in range(3):
            for dx in range(2):
                if self.grid[top_lcy + dy][top_lcx + dx] & self.EAST:
                    return False
        for dx in range(3):
            for dy in range(2):
                if self.grid[top_lcy + dy][top_lcx + dx] & self.SOUTH:
                    return False
        return True

    def _outer_spaces_playable(self) -> None:
        """Configure outer boundary walls for the maze layout.
           The four corners must stay open corridors, so each corner keeps only
           its two border walls and the two neighbouring cells are updated to
           match. Skipped on a maze thinner than two cells, which has no corner
           to open."""

        if self.width < 2 or self.height < 2:
            return

        w = self.width - 1
        h = self.height - 1

        self.grid[0][0] = self.NORTH | self.WEST
        self.grid[1][0] &= ~self.NORTH
        self.grid[0][1] &= ~self.WEST

        self.grid[0][w] = self.NORTH | self.EAST
        self.grid[0][w - 1] &= ~self.EAST
        self.grid[1][w] &= ~self.NORTH

        self.grid[h][0] = self.SOUTH | self.WEST
        self.grid[h][1] &= ~self.WEST
        self.grid[h - 1][0] &= ~self.SOUTH

        self.grid[h][w] = self.SOUTH | self.EAST
        self.grid[h][w - 1] &= ~self.EAST
        self.grid[h - 1][w] &= ~self.SOUTH

    def _dead_ends_out(self, seed: int) -> None:
        """Remove dead ends to create alternative paths and loops.

        Opening a wall never turns another cell into a dead end, so one pass
        over the dead ends found at the start is enough: a cell that stopped
        being a dead end meanwhile is simply skipped. The only dead ends left
        are the pockets of the "42" pattern, whose closed walls are all
        shared with pattern cells.

        Args:
            seed (int): Random seed for dead-end selection.
        """
        rnd = random.Random(seed)
        dead_ends = self._find_dead_ends()
        rnd.shuffle(dead_ends)

        for x, y in dead_ends:
            if self.grid[y][x].bit_count() != 3:
                continue
            self._open_dead_end(x, y)

    def _open_dead_end(self, x: int, y: int) -> bool:
        """Open one closed wall of a dead-end cell towards a cell outside the
        "42" pattern, keeping the no-3x3-open-area rule.

        Args:
            x, y (int): Coordinates of the dead-end cell.

        Returns:
            bool: True if one wall could be opened.
        """
        for dx, dy, wall, opp_wall in self.DIRECTIONS:
            nx, ny = x + dx, y + dy

            if not self.grid[y][x] & wall:
                continue
            if not (0 <= nx < self.width and 0 <= ny < self.height):
                continue
            if (nx, ny) in self.pattern:
                continue

            if self._try_open_wall(x, y, nx, ny, wall, opp_wall):
                return True
        return False

    def _find_dead_ends(self) -> List[Tuple[int, int]]:
        """Return the coordinates of every current dead-end cell (a cell
        with only one opening), excluding cells in the "42" pattern.

        Returns:
            List[Tuple[int, int]]: Coordinates of dead-end cells.
        """
        return [
            (x, y)
            for y in range(self.height)
            for x in range(self.width)
            if (x, y) not in self.pattern and
            self.grid[y][x].bit_count() == 3
        ]

    def get_grid(self) -> List[List[int]]:
        """Return a deep copy of the current maze grid.

        Returns:
            List[List[int]]: A 2D list representing the maze grid.
        """
        return [row[:] for row in self.grid]

    def generate_grid(self, entry_x: int, entry_y: int, seed: int,
                      perfect: bool = False) -> None:
        """Generate the maze grid using either perfect or playable algorithms.

        Args:
            entry_x (int): X-coordinate of the entry point.
            entry_y (int): Y-coordinate of the entry point.
            seed (int): Random seed for generation.
            perfect (bool, optional): Whether to generate a strict perfect maze
                Defaults to False.

        Raises:
            ValueError: If entry coordinates are out of bounds or inside the
            closed "42" pattern..
        """
        if not (0 <= entry_x < self.width and 0 <= entry_y < self.height):
            raise ValueError(f"Entry coordinates ({entry_x}, {entry_y}) are"
                             f"out of bounds for maze size {self.width}"
                             f"x{self.height}.")
        if (entry_x, entry_y) in self.pattern:
            raise ValueError(f"Entry coordinates ({entry_x}, {entry_y}) are "
                             f"inside the '42' pattern, which stays fully"
                             f" closed.")
        if not perfect:
            self.create_playable_maze(entry_x, entry_y, seed)
        else:
            self._perfect_maze(entry_x, entry_y, seed)

    def path_finder_bfs(self, entry: Tuple[int, int], exit_:
                        Tuple[int, int]) -> List[Tuple[int, int]]:
        """Find the shortest path between entry and exit using
        Breadth-First Search.

        Args:
            entry (Tuple[int, int]): Starting coordinates (x, y).
            exit_ (Tuple[int, int]): Target coordinates (x, y).

        Returns:
            List[Tuple[int, int]]: Ordered list of coordinate tuples forming
            the path, empty if there is no path or a coordinate is invalid.
        """
        entry_x, entry_y = entry
        exit_x, exit_y = exit_
        w = self.width
        h = self.height

        if not (0 <= entry_x < w and 0 <= entry_y < h):
            return []
        if not (0 <= exit_x < w and 0 <= exit_y < h):
            return []

        queue = deque([(entry_x, entry_y)])
        visited: Set[Tuple[int, int]] = {(entry_x, entry_y)}
        path_before: Dict[Tuple[int, int], Tuple[int, int]] = {}
        bfs_directions = [
            (0, -1, self.NORTH), (1, 0, self.EAST), (0, 1, self.SOUTH),
            (-1, 0, self.WEST)
        ]

        while queue:
            cx, cy = queue.popleft()
            if (cx, cy) == (exit_x, exit_y):
                break
            for dx, dy, wall in bfs_directions:
                nx, ny = cx + dx, cy + dy
                if 0 <= nx < w and 0 <= ny < h:
                    if ((self.grid[cy][cx] & wall) == 0 and (nx, ny) not in
                            visited):
                        visited.add((nx, ny))
                        path_before[(nx, ny)] = (cx, cy)
                        queue.append((nx, ny))

        if (exit_x, exit_y) not in visited and (exit_x, exit_y) != (entry_x,
                                                                    entry_y):
            return []

        path = [(exit_x, exit_y)]
        while path[-1] != (entry_x, entry_y):
            path.append(path_before[path[-1]])
        path.reverse()
        return path
