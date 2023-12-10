from enum import Enum
from pathlib import Path
from pprint import pprint
from typing import Iterable, Self

import numpy as np

Loc = tuple[int, int]
PipeGrid = np.ndarray  # 2-dimensional array of single-char strings

START = "S"
EMPTY = "."

INPUT_FILE_PATH = Path("input.txt")


def _find_start(grid: PipeGrid) -> Loc:
    for r, row in enumerate(grid):
        for c, char in enumerate(row):
            if char == START:
                return r, c
    else:
        raise ValueError("start location not found")


class Direction(Enum):
    UP = (-1, 0)
    LEFT = (0, -1)
    RIGHT = (0, 1)
    DOWN = (1, 0)

    def opposite(self) -> Self:
        r, c = self.value
        return self.__class__((-1 * r, -1 * c))

    def clockwise(self) -> Self:
        r, c = self.value
        return self.__class__((c, -1 * r))

    def counter_clockwise(self) -> Self:
        r, c = self.value
        return self.__class__((-1 * c, r))


def shift(loc: Loc, direction: Direction) -> Loc:
    r_shift, c_shift = direction.value
    return loc[0] + r_shift, loc[1] + c_shift


class Pipe(Enum):
    UL = "J"
    UR = "L"
    UD = "|"
    LR = "-"
    LD = "7"
    RD = "F"

    def to_directions(self) -> tuple[Direction, Direction]:
        dict_ = {
            self.UL: (Direction.UP, Direction.LEFT),
            self.UR: (Direction.UP, Direction.RIGHT),
            self.UD: (Direction.UP, Direction.DOWN),
            self.LR: (Direction.LEFT, Direction.RIGHT),
            self.LD: (Direction.LEFT, Direction.DOWN),
            self.RD: (Direction.RIGHT, Direction.DOWN),
        }
        d1, d2 = sorted(dict_[self], key=lambda d: d.value)
        return d1, d2

    @classmethod
    def from_directions(cls, directions: tuple[Direction, Direction]) -> Self:
        d1, d2 = sorted(directions, key=lambda d: d.value)
        dict_ = {
            (Direction.UP, Direction.LEFT): cls.UL,
            (Direction.UP, Direction.RIGHT): cls.UR,
            (Direction.UP, Direction.DOWN): cls.UD,
            (Direction.LEFT, Direction.RIGHT): cls.LR,
            (Direction.LEFT, Direction.DOWN): cls.LD,
            (Direction.RIGHT, Direction.DOWN): cls.RD,
        }
        return dict_[(d1, d2)]


def read_input() -> tuple[PipeGrid, Loc]:
    # read raw input
    with open(INPUT_FILE_PATH, "r", encoding="utf-8") as f:
        grid = np.array([
            list(line.strip())
            for line in f
        ])
    # pad for convenience
    grid = np.pad(grid, 1, constant_values=EMPTY)
    # find the start symbol and figure out what kind of pipe it is
    start_loc = _find_start(grid)
    start_directions = set()
    for direction in Direction:
        neighbor_loc = shift(start_loc, direction)
        neighbor = grid[neighbor_loc]
        if neighbor != EMPTY and direction.opposite() in Pipe(neighbor).to_directions():
            start_directions.add(direction)
    assert len(start_directions) == 2
    start_pipe = Pipe.from_directions(start_directions)
    # overwrite the start symbol with its actual pipe symbol
    grid[start_loc] = start_pipe.value
    return grid, start_loc


def neighbors(loc: Loc) -> Iterable[Loc]:
    for direction in Direction:
        yield shift(loc, direction)


def solve1(grid: PipeGrid, start_loc: Loc) -> tuple[int, set[Loc]]:
    loop_locs = {start_loc}
    cur_locs = {start_loc}
    while True:
        cur_locs = {
            shift(cur_loc, direction)
            for cur_loc in cur_locs
            for direction in Pipe(grid[cur_loc]).to_directions()
        }
        cur_locs -= loop_locs
        loop_locs.update(cur_locs)
        n_cur_locs = len(cur_locs)
        assert 1 <= n_cur_locs <= 2
        if n_cur_locs == 1:
            break  # the two paths met
    # loop completed
    loop_size = len(loop_locs)
    half, remainder = divmod(loop_size, 2)
    assert remainder == 0
    return half, loop_locs


def solve2(grid: PipeGrid, loop_locs: set[Loc]) -> int:
    n_inside = 0
    is_loop = np.array([
        [
            (r, c) in loop_locs
            for c in range(grid.shape[1])
        ]
        for r in range(grid.shape[0])
    ])
    is_inside = np.zeros(grid.shape[1], dtype=bool)
    for row, is_loop_row in zip(grid, is_loop):
        could_be_crossing = np.array([
            Pipe(symbol) in (Pipe.UL, Pipe.LR, Pipe.LD)
                if symbol != EMPTY
                else False
            for symbol in row
        ])
        is_crossing = np.logical_and(could_be_crossing, is_loop_row)
        is_inside = np.where(is_crossing, np.logical_not(is_inside), is_inside)
        is_inside_fully = np.logical_and(is_inside, np.logical_not(is_loop_row))
        n_inside += np.count_nonzero(is_inside_fully)
    return n_inside


def main():
    grid, start_loc = read_input()
    answer, loop_locs = solve1(grid, start_loc)
    pprint(answer)
    answer = solve2(grid, loop_locs)
    pprint(answer)


if __name__ == "__main__":
    main()
