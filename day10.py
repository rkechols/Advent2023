from pathlib import Path
from pprint import pprint
from typing import Iterable, Self
import numpy as np
from enum import Enum

Input = np.ndarray

INPUT_FILE_PATH = Path("input.txt")

Loc = tuple[int, int]
START = "S"
EMPTY = "."


def read_input() -> Input:
    with open(INPUT_FILE_PATH, "r", encoding="utf-8") as f:
        return np.pad(np.array([
            list(line.strip())
            for line in f
        ]), 1, constant_values=".")


class Direction(Enum):
    RIGHT = (0, 1)
    UP = (-1, 0)
    LEFT = (0, -1)
    DOWN = (1, 0)

    def opposite(self) -> Self:
        if self == self.RIGHT:
            return self.LEFT
        if self == self.LEFT:
            return self.RIGHT
        if self == self.UP:
            return self.DOWN
        if self == self.DOWN:
            return self.UP
        raise ValueError


def shift(loc: Loc, direction: Direction) -> Loc:
    r_shift, c_shift = direction.value
    return loc[0] + r_shift, loc[1] + c_shift


def symbol_to_directions(sym: str) -> tuple[Direction, Direction]:
    if sym == "-":
        return Direction.LEFT, Direction.RIGHT
    if sym == "|":
        return Direction.UP, Direction.DOWN
    if sym == "F":
        return Direction.RIGHT, Direction.DOWN
    if sym == "7":
        return Direction.LEFT, Direction.DOWN
    if sym == "J":
        return Direction.LEFT, Direction.UP
    if sym == "L":
        return Direction.RIGHT, Direction.UP
    raise ValueError("symbol was not a tunnel shape")


def find_start(grid: np.ndarray) -> Loc:
    for r, row in enumerate(grid):
        for c, char in enumerate(row):
            if char == START:
                return r, c
    else:
        raise ValueError("start location not found")


def neighbors(loc: Loc) -> Iterable[Loc]:
    for direction in Direction:
        yield shift(loc, direction)


def solve(input_: Input) -> int:
    start = find_start(input_)
    start_neighbor_locs = set()
    for direction in Direction:
        neighbor_loc = shift(start, direction)
        neighbor = input_[neighbor_loc]
        if neighbor != EMPTY and direction.opposite() in symbol_to_directions(neighbor):
            start_neighbor_locs.add(neighbor_loc)
    assert len(start_neighbor_locs) == 2
    loop_locs = {start} | start_neighbor_locs
    cur_locs = start_neighbor_locs
    while True:
        neighbor_locs = {
            shift(cur_loc, direction)
            for cur_loc in cur_locs
            for direction in symbol_to_directions(input_[cur_loc])
        } - loop_locs
        loop_locs.update(neighbor_locs)
        n = len(neighbor_locs)
        if n == 0:
            raise ValueError("idk")
        elif n == 1:
            loop_size = len(loop_locs)
            half, remainder = divmod(loop_size, 2)
            assert remainder == 0
            return half
        elif n == 2:
            cur_locs = neighbor_locs
        else:
            raise ValueError("idk 2")


def main():
    input_ = read_input()
    answer = solve(input_)
    pprint(answer)


if __name__ == "__main__":
    main()
