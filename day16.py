from pathlib import Path
from collections import defaultdict
from pprint import pprint
from enum import Enum
from typing import Iterable, Optional

import numpy as np


class Direction(Enum):
    UP = (-1, 0)
    LEFT = (0, -1)
    DOWN = (1, 0)
    RIGHT = (0, 1)


class Mirror(Enum):
    EMPTY = "."
    NW = "\\"
    NE = "/"
    VERT = "|"
    HORIZ = "-"

    def reflect(self, direction: Direction) -> set[Direction]:
        direction_tup = direction.value
        if self == self.EMPTY:
            return {direction}  # no change
        elif self == self.NW:
            return {Direction((direction_tup[1], direction_tup[0]))}
        elif self == self.NE:
            return {Direction((-1 * direction_tup[1], -1 * direction_tup[0]))}
        elif self == self.VERT:
            split_dirs = {Direction.UP, Direction.DOWN}
        elif self == self.HORIZ:
            split_dirs = {Direction.LEFT, Direction.RIGHT}
        else:
            raise ValueError(f"unrecognized direction: {direction}")
        if direction in split_dirs:
            return {direction}  # no change
        else:
            return split_dirs


Input = np.ndarray

INPUT_FILE_PATH = Path("input.txt")


def read_input() -> Input:
    with open(INPUT_FILE_PATH, "r", encoding="utf-8") as f:
        return np.array([
            [Mirror(sym) for sym in line.strip()]
            for line in f
        ])


def solve1(grid: Input, *, start_loc: tuple[int, int] = (0, 0), start_direction: Direction = Direction.RIGHT) -> int:
    energized_locs_with_dirs = defaultdict(set)
    energized_locs_with_dirs[start_loc].add(start_direction)
    search_queue = {(start_loc, start_direction)}
    while len(search_queue) > 0:
        loc, direction = search_queue.pop()
        mirror = grid[loc]
        for new_direction in mirror.reflect(direction):
            new_loc: tuple[int, int] = tuple(d + shift for d, shift in zip(loc, new_direction.value))
            if any(not (0 <= d < limit) for d, limit in zip(new_loc, grid.shape)):
                continue  # off-grid
            if new_direction in energized_locs_with_dirs[new_loc]:
                continue  # in a cycle
            # mark it as energized and make sure we add it to the queue for further expansion
            energized_locs_with_dirs[new_loc].add(new_direction)
            search_queue.add((new_loc, new_direction))
    return sum(len(dirs) > 0 for dirs in energized_locs_with_dirs.values())


def solve2(grid: Input) -> int:
    n_rows, n_cols = grid.shape
    last_row, last_col = n_rows - 1, n_cols - 1
    def gen_all() -> Iterable[int]:
        for row in range(n_rows):
            yield solve1(grid, start_loc=(row, 0), start_direction=Direction.RIGHT)
            yield solve1(grid, start_loc=(row, last_col), start_direction=Direction.LEFT)
        for col in range(n_cols):
            yield solve1(grid, start_loc=(0, col), start_direction=Direction.DOWN)
            yield solve1(grid, start_loc=(last_row, col), start_direction=Direction.UP)
    data = list(gen_all())
    return max(data)



def main():
    input_ = read_input()
    answer = solve1(input_)
    pprint(answer)
    answer = solve2(input_)
    pprint(answer)


if __name__ == "__main__":
    main()
