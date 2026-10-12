import random
import sys
from typing import Callable, Dict
from maze_config import ConfigError, MazeConfig, parse_config
from maze_generator import MazeGenerator
from maze_model import Maze
from maze_view import run_viewer
from maze_write import write_output


def _build_maze(config: MazeConfig, seed: int) -> Maze:
    gen = MazeGenerator(config.width, config.height)
    gen.generate_grid(
        config.entry[0], config.entry[1], seed, perfect=config.perfect
    )
    grid = gen.get_grid()
    path = gen.path_finder_bfs(config.entry, config.exit)
    return Maze(
        config.width, config.height, grid, config.entry, config.exit, path
    )


def _first_then_regenerate(
    config: MazeConfig, first: Maze
) -> Callable[[], Maze]:
    state: Dict[str, object] = {"maze": first, "used": False}

    def factory() -> Maze:
        if not state["used"]:
            state["used"] = True
        else:
            seed = random.randrange(2**31)
            state["maze"] = _build_maze(config, seed)
        return state["maze"]  # type: ignore[return-value]

    return factory


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print(f"Usage: python3 {argv[0]} config.txt", file=sys.stderr)
        return 1

    try:
        config = parse_config(argv[1])
    except (ConfigError, ValueError, OSError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    initial_seed = (
        config.seed if config.seed is not None else random.randrange(2**31)
    )
    maze = _build_maze(config, initial_seed)
    try:
        write_output(maze, config.output_file)
    except OSError as exc:
        print(f"Error writing output file: {exc}", file=sys.stderr)
        return 1
    run_viewer(_first_then_regenerate(config, maze))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
