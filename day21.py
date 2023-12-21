from enum import Enum
from pathlib import Path
from pprint import pprint

import numpy as np

Loc = tuple[int, int]
Input = tuple[np.ndarray, Loc]  # 2D, bools

INPUT_FILE_PATH = Path("input.txt")

START = "S"
ROCK = "#"


class Direction(Enum):
    RIGHT = (1, 0)
    DOWN = (0, -1)
    LEFT = (-1, 0)
    UP = (0, 1)

    def shift(self, loc: Loc) -> Loc:
        new_loc = tuple(d + s for d, s in zip(loc, self.value))
        return new_loc


def read_input() -> Input:
    grid = []
    start_loc = None
    with open(INPUT_FILE_PATH, "r", encoding="utf-8") as f:
        for r, line_ in enumerate(f):
            line = line_.strip()
            for c, s in enumerate(line):
                if s == START:
                    start_loc = (r, c)
            row = [s != ROCK for s in line]
            grid.append(row)
    grid = np.array(grid)
    return grid, start_loc


def solve1(input_: Input, n_steps: int) -> int:
    grid, start_loc = input_
    # pad with all rocks to simplify out-of-bounds checking
    grid = np.pad(grid, 1, constant_values=False)
    start_loc = tuple(d + 1 for d in start_loc)
    # BFS-like search
    parity = n_steps % 2
    seen_locs: set[Loc] = set()  # don't repeat / backtrack into known territory
    possible_locs: set[Loc] = set()  # answer
    search_locs = {start_loc}  # "queue" of current possible positions
    for step_num in range(n_steps + 1):
        if step_num % 2 == parity:
            possible_locs.update(search_locs)
        seen_locs.update(search_locs)
        search_locs_next = set()  # next layer of possible positions
        for search_loc in search_locs:
            for direction in Direction:
                neighbor_loc = direction.shift(search_loc)
                if grid[neighbor_loc] and neighbor_loc not in seen_locs:
                    search_locs_next.add(neighbor_loc)
        search_locs = search_locs_next
    return len(possible_locs)


BoardLoc = tuple[int, int]
InfiniteLoc = tuple[Loc, BoardLoc]


def solve2(input_: Input, n_steps: int) -> int:
    grid, start_loc = input_

    def wrap_loc(infinite_loc: InfiniteLoc) -> InfiniteLoc:
        loc, board_loc = infinite_loc
        loc_new = tuple(d % n for d, n in zip(loc, grid.shape))
        board_loc_new = tuple(b + (d // n) for d, b, n in zip(loc, board_loc, grid.shape))
        return loc_new, board_loc_new

    parity = n_steps % 2
    seen_locs: set[InfiniteLoc] = set()
    possible_locs: set[InfiniteLoc] = set()
    search_locs: set[InfiniteLoc] = {(start_loc, (0, 0))}
    for step_num in range(n_steps + 1):
        if step_num % 2 == parity:
            possible_locs.update(search_locs)
        seen_locs.update(search_locs)
        search_locs_next = set()
        for search_loc in search_locs:
            for direction in Direction:
                loc, board_loc = search_loc
                neighbor_loc = direction.shift(loc)
                neighbor_inf_loc = wrap_loc((neighbor_loc, board_loc))
                if grid[neighbor_inf_loc[0]] and neighbor_inf_loc not in seen_locs:
                    search_locs_next.add(neighbor_inf_loc)
        search_locs = search_locs_next
    return len(possible_locs)


def main():
    input_ = read_input()
    answer = solve1(input_, n_steps=64)
    pprint(answer)
    # answer = solve2(input_, n_steps=1000)
    answer = solve2(input_, n_steps=26501365)
    pprint(answer)


if __name__ == "__main__":
    main()
