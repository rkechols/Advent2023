from pathlib import Path
from pprint import pprint
from enum import Enum
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
    # pad with all rocks to simplify out-of-bounds checking
    grid = np.pad(grid, 1, constant_values=False)
    start_loc = tuple(d + 1 for d in start_loc)
    return np.array(grid), start_loc


def manhattan(loc1: Loc, loc2: Loc) -> int:
    return sum(abs(d1 - d2) for d1, d2 in zip(loc1, loc2))


def solve(input_: Input, n_steps: int) -> int:
    grid, start_loc = input_
    parity = n_steps % 2
    seen_locs: set[Loc] = set()
    possible_locs: set[Loc] = set()
    search_locs = {start_loc}
    for step_num in range(n_steps + 1):
        if step_num % 2 == parity:
            possible_locs.update(search_locs)
        seen_locs.update(search_locs)
        search_locs_next = set()
        for search_loc in search_locs:
            for direction in Direction:
                neighbor_loc = direction.shift(search_loc)
                if grid[neighbor_loc] and neighbor_loc not in seen_locs:
                    search_locs_next.add(neighbor_loc)
        search_locs = search_locs_next
    return len(possible_locs)


def main():
    input_ = read_input()
    answer = solve(input_, n_steps=64)
    pprint(answer)


if __name__ == "__main__":
    main()
