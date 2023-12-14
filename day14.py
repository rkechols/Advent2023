from pathlib import Path
from pprint import pprint

import numpy as np

Input = np.ndarray  # each slot is a single char

INPUT_FILE_PATH = Path("input.txt")

EMPTY = "."
ROCK_STATIC = "#"
ROCK_MOBILE = "O"


def read_input() -> Input:
    with open(INPUT_FILE_PATH, "r", encoding="utf-8") as f:
        return np.array([
            list(line)
            for line_ in f
            if (line := line_.strip()) != ""
        ])


def tilt_north(grid: np.ndarray) -> np.ndarray:
    grid = grid.copy()
    for c in range(grid.shape[1]):
        r_last_obstacle = -1
        for r in range(grid.shape[0]):
            obj = grid[r, c]
            if obj == EMPTY:
                continue
            elif obj == ROCK_STATIC:
                r_last_obstacle = r
            elif obj == ROCK_MOBILE:
                # rolls up
                grid[r, c] = EMPTY
                r_destination = r_last_obstacle + 1
                grid[r_destination, c] = ROCK_MOBILE
                r_last_obstacle = r_destination
            else:
                raise ValueError(f"grid[{r}, {c}] has unexpected value {obj!r}")
    return grid


def solve1(grid: Input) -> int:
    # tilt everything north
    grid = tilt_north(grid)
    # scores
    total_load = 0
    for load, row in enumerate(grid[::-1], start=1):
        count = np.count_nonzero(row == ROCK_MOBILE)
        total_load += count * load
    return total_load


def solve2(grid: Input, *, n_cycles: int) -> int:
    seen_states_by_rotation = {rot: {} for rot in range(4)}
    has_skipped = False
    i_cycle = 0
    while i_cycle < n_cycles:
        for rot in range(4):
            grid = tilt_north(grid)
            grid = np.rot90(grid, k=-1)
            if has_skipped:
                continue  # don't bother checking or updating anything for cycle detection
            grid_str = "\n".join("".join(row) for row in grid)
            seen_states = seen_states_by_rotation[rot]
            last_seen = seen_states.get(grid_str)
            if last_seen is None:
                seen_states[grid_str] = i_cycle
            else:  # seen it before
                period = i_cycle - last_seen
                # print(f"cycle {i_cycle} rotation {rot} was equivalent to the same rotation of cycle {last_seen}")
                # print(f"({period=})")
                n_periods_to_skip = (n_cycles - i_cycle - 1) // period
                n_cycles_to_skip = n_periods_to_skip * period
                # print(f"{n_cycles_to_skip=}")
                i_cycle += n_cycles_to_skip
                has_skipped = True
        i_cycle += 1
    # scores
    total_load = 0
    for load, row in enumerate(grid[::-1], start=1):
        count = np.count_nonzero(row == ROCK_MOBILE)
        total_load += count * load
    return total_load


def main():
    input_ = read_input()
    answer = solve1(input_)
    pprint(answer)
    answer = solve2(input_, n_cycles=1_000_000_000)
    pprint(answer)


if __name__ == "__main__":
    main()
