"""Shared maze data contract, used by the generator, writer and viewer."""

from dataclasses import dataclass
from typing import List, Tuple

NORTH, EAST, SOUTH, WEST = 1, 2, 4, 8


@dataclass
class Maze:
    width: int
    height: int
    grid: List[List[int]]
    entry: Tuple[int, int]
    exit: Tuple[int, int]
    path: List[Tuple[int, int]]
