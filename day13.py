from pathlib import Path
from pprint import pprint

import numpy as np

Input = list[np.ndarray]

INPUT_FILE_PATH = Path("input.txt")

ROCK = "#"


def read_input() -> Input:
    with open(INPUT_FILE_PATH, "r", encoding="utf-8") as f:
        f_contents = f.read().strip()
    blocks = f_contents.split("\n\n")
    blocks = [
        np.array([
            [c == ROCK for c in line]
            for line_ in block.split("\n")
            if (line := line_.strip()) != ""
        ])
        for block in blocks
    ]
    return blocks


def _find_reflection_row_smudge(grid: np.ndarray, *, smudges: int) -> int | None:
    assert len(grid.shape) == 2
    n_rows = grid.shape[0]
    assert n_rows > 1
    for i in range(1, n_rows):
        n_below = n_rows - i
        n_mirrorable = min(i, n_below)
        grid_above = grid[(i - n_mirrorable):i]
        grid_below = grid[(i + n_mirrorable - 1):(i - 1):-1]
        if np.count_nonzero(grid_above != grid_below) == smudges:
            return i
    return None


def solve(input_: Input, *, smudges: int = 0) -> int:
    total = 0
    for i, grid in enumerate(input_):
        reflection_row = _find_reflection_row_smudge(grid, smudges=smudges)
        if reflection_row is not None:
            total += 100 * reflection_row
            continue
        reflection_col = _find_reflection_row_smudge(grid.T, smudges=smudges)
        if reflection_col is not None:
            total += reflection_col
            continue
        raise ValueError(f"no reflection found (grid index {i})")
    return total


def main():
    input_ = read_input()
    answer = solve(input_)
    pprint(answer)
    answer = solve(input_, smudges=1)
    pprint(answer)


if __name__ == "__main__":
    main()
