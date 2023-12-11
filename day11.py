from pathlib import Path
import itertools
from pprint import pprint
import numpy as np
from typing import Any

Input = np.ndarray  # feel free to change per-problem; whatever structure is easiest

INPUT_FILE_PATH = Path("input.txt")

GALAXY = "#"


def read_input() -> Input:
    with open(INPUT_FILE_PATH, "r", encoding="utf-8") as f:
        return np.array([
            [c == GALAXY for c in line.strip()]
            for line in f
        ], dtype=bool)


def expand_space(grid: np.ndarray) -> np.ndarray:
    # rows
    i = 0
    while i < grid.shape[0]:
        row = grid[i]
        if np.count_nonzero(row) == 0:
            row_duplicated = np.stack([row, row], axis=0)
            grid = np.concatenate(
                [grid[:i], row_duplicated, grid[(i + 1):]],
                axis=0,
            )
            i += 2
        else:
            i += 1
    # cols
    j = 0
    while j < grid.shape[1]:
        col = grid[:, j]
        if np.count_nonzero(col) == 0:
            col_duplicated = np.stack([col, col], axis=1)
            grid = np.concatenate(
                [grid[:, :j], col_duplicated, grid[:, (j + 1):]],
                axis=1,
            )
            j += 2
        else:
            j += 1
    return grid


def solve(grid: Input) -> int:
    grid = expand_space(grid)
    galaxy_locs = set()
    for loc in itertools.product(range(grid.shape[0]), range(grid.shape[1])):
        if grid[loc]:
            galaxy_locs.add(loc)
    galaxy_locs = sorted(galaxy_locs)
    total = 0
    for i, loc1 in enumerate(galaxy_locs):
        for loc2 in galaxy_locs[(i + 1):]:
            i_dist = abs(loc1[0] - loc2[0])
            j_dist = abs(loc1[1] - loc2[1])
            grid_dist = i_dist + j_dist
            total += grid_dist
    return total


def main():
    input_ = read_input()
    answer = solve(input_)
    pprint(answer)


if __name__ == "__main__":
    main()
