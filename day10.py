from enum import Enum
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
    start_direction = None
    for direction in Direction:
        neighbor_loc = shift(start, direction)
        neighbor = grid[neighbor_loc]
        if neighbor != EMPTY and direction.opposite() in symbol_to_directions(neighbor):
            start_direction = direction
            break
    assert start_direction is not None
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


def solve2(grid: np.ndarray, loop: list[tuple[Loc, Direction]]) -> int:
    # what direction is the loop rotating as a whole
    cross_sum = 0
    for i, (_, direction) in enumerate(loop):
        prev_direction = loop[i - 1][1]
        if direction == prev_direction:
            continue  # nothing of note
        a1, a2 = prev_direction.value
        b1, b2 = direction.value
        cross = (a1 * b2) - (a2 * b1)
        cross_sum += cross
    assert abs(cross_sum) == 4
    if cross_sum > 0:
        direction_to_inside = Direction.counter_clockwise
    else:
        direction_to_inside = Direction.clockwise
    # start searches from all locations just inside the loop
    loop_locs = {loop_loc for loop_loc, _ in loop}
    inside_locs = set()
    for loop_loc, loop_direction in loop:
        bfs_locs = {shift(loop_loc, direction_to_inside(loop_direction))}
        while len(bfs_locs) > 0:
            search_loc = bfs_locs.pop()
            if search_loc not in loop_locs and search_loc not in inside_locs:
                inside_locs.add(search_loc)
                bfs_locs.update(shift(search_loc, direction) for direction in Direction)
    return len(inside_locs)


def main():
    input_ = read_input()
    answer, loop = solve1(input_)
    pprint(answer)
    answer = solve2(input_, loop)
    pprint(answer)


if __name__ == "__main__":
    main()
