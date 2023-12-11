import itertools
from pathlib import Path
from pprint import pprint

import numpy as np

Input = np.ndarray  # feel free to change per-problem; whatever structure is easiest

INPUT_FILE_PATH = Path("input.txt")

GALAXY = "#"


def read_input() -> Input:
    with open(INPUT_FILE_PATH, "r", encoding="utf-8") as f:
        return np.array([
            [c == GALAXY for c in line.strip()]
            for line in f
        ], dtype=bool)


def grid_to_locs(grid: np.ndarray) -> list[tuple[int, int]]:
    galaxy_locs = []
    for loc in itertools.product(range(grid.shape[0]), range(grid.shape[1])):
        if grid[loc]:
            galaxy_locs.append(loc)
    return galaxy_locs


def expand_space(locs: list[tuple[int, int]], *, expansion: int) -> list[tuple[int, int]]:
    if expansion < 0:
        raise ValueError("expansion undefined for negative values")
    if expansion == 1:
        return locs
    # use numpy array for vectorized operations
    # NOTE: integer overflow is possible, but numpy will give a RuntimeWarning if it does.
    #    To avoid any possible overflow, stay with python built-in types like `list` and `int`
    locs = np.array(locs, dtype=np.int64)  # shape (n, 2)
    size_diff = expansion - 1
    for axis in range(locs.shape[1]):
        i = 0
        while i < locs[:, axis].max():
            if np.count_nonzero(locs[:, axis] == i) == 0:
                locs[locs[:, axis] > i, axis] += size_diff
                i += size_diff  # move cursor to last new index
            i += 1  # move on
    # convert output
    return [tuple(loc) for loc in locs]


def solve(grid: Input, *, expansion: int) -> int:
    galaxy_locs = grid_to_locs(grid)
    galaxy_locs = expand_space(galaxy_locs, expansion=expansion)
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
    answer = solve(input_, expansion=2)
    pprint(answer)
    answer = solve(input_, expansion=1_000_000)
    pprint(answer)


if __name__ == "__main__":
    main()
