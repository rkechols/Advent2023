from enum import Enum
import itertools
from pathlib import Path
from pprint import pprint
from typing import Iterable, Self

import numpy as np

INPUT_FILE_PATH = Path("input.txt")

Loc = tuple[int, int]
START = "S"
EMPTY = "."


def read_input() -> np.ndarray:
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


def solve1(grid: np.ndarray) -> tuple[int, list[tuple[Loc, Direction]]]:
    start = find_start(grid)
    start_directions = set()
    for direction in Direction:
        neighbor_loc = shift(start, direction)
        neighbor = grid[neighbor_loc]
        if neighbor != EMPTY and direction.opposite() in symbol_to_directions(neighbor):
            start_directions.add(direction)
    if start_directions == {Direction.LEFT, Direction.UP}:
        start_symbol = "J"
    elif start_directions == {Direction.LEFT, Direction.DOWN}:
        start_symbol = "7"
    elif start_directions == {Direction.RIGHT, Direction.UP}:
        start_symbol = "L"
    elif start_directions == {Direction.RIGHT, Direction.DOWN}:
        start_symbol = "F"
    elif start_directions == {Direction.LEFT, Direction.RIGHT}:
        start_symbol = "-"
    elif start_directions == {Direction.UP, Direction.DOWN}:
        start_symbol = "|"
    else:
        raise ValueError("🫠")
    grid[start] = start_symbol
    start_direction = next(iter(start_directions))
    loop = [(start, start_direction)]
    loc = shift(start, start_direction)
    while loc != start:
        for direction in symbol_to_directions(grid[loc]):
            new_loc = shift(loc, direction)
            if new_loc != loop[-1][0]:  # don't go backward
                # figured out what direction to go from here; write it down and do it
                loop.append((loc, direction))
                loc = new_loc
                break
        else:
            raise ValueError("idk")
    # loop completed
    loop_size = len(loop)
    half, remainder = divmod(loop_size, 2)
    assert remainder == 0
    return half, loop


def print_grid(grid: np.ndarray):
    print("\n".join("".join(row) for row in grid))


def solve2(grid: np.ndarray, loop: list[tuple[Loc, Direction]]) -> int:
    canvas = np.array([[" " for _ in range(grid.shape[1])] for _ in range(grid.shape[0])])
    for loop_loc, _ in loop:
        canvas[loop_loc] = grid[loop_loc]
    loop_locs = {loop_loc for loop_loc, _ in loop}
    n_inside = 0
    for search_start_loc in itertools.product(*(range(dim_size) for dim_size in grid.shape)):
        if search_start_loc in loop_locs:
            continue
        n_crossings = 0
        search_loc = search_start_loc
        while (search_loc := shift(search_loc, Direction.UP))[0] > 0:
            if search_loc in loop_locs:
                symbol = grid[search_loc]
                if symbol in "-J7":
                    n_crossings += 1
                elif symbol not in "|FL":
                    raise ValueError(f"symbol {symbol!r} should not be part of the loop")
        if n_crossings % 2 != 0:  # odd crossing; we were inside
            n_inside += 1
    return n_inside


def main():
    input_ = read_input()
    answer, loop = solve1(input_)
    pprint(answer)
    answer = solve2(input_, loop)
    pprint(answer)


if __name__ == "__main__":
    main()
