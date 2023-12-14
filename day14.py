from math import e
from pathlib import Path
from pprint import pprint
from typing import Any
import numpy as np

Input = np.ndarray  # each slot is a single char

INPUT_FILE_PATH = Path("input.txt")

EMPTY = "."
ROCK = "#"
BALL = "O"


def read_input() -> Input:
    with open(INPUT_FILE_PATH, "r", encoding="utf-8") as f:
        return np.array([
            list(line)
            for line_ in f
            if (line := line_.strip()) != ""
        ])


def solve(input_: Input) -> int:
    grid = input_.copy()
    # tilt everything north
    for c in range(grid.shape[1]):
        r_last_obstacle = -1
        for r in range(grid.shape[0]):
            obj = grid[r, c]
            if obj == EMPTY:
                continue
            elif obj == ROCK:
                r_last_obstacle = r
            elif obj == BALL:
                # rolls up
                grid[r, c] = EMPTY
                r_destination = r_last_obstacle + 1
                grid[r_destination, c] = BALL
                r_last_obstacle = r_destination
            else:
                raise ValueError(f"grid[{r}, {c}] has unexpected value {obj!r}")
    # scores
    total_load = 0
    for load, row in enumerate(grid[::-1], start=1):
        count = np.count_nonzero(row == BALL)
        total_load += count * load
    return total_load


def main():
    input_ = read_input()
    answer = solve(input_)
    pprint(answer)


if __name__ == "__main__":
    main()
