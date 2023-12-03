import copy
import numpy as np
from pathlib import Path
from pprint import pprint
from typing import Any, Sequence

EMPTY = "."

Input = list[list[str]]

INPUT_FILE_PATH = Path("input.txt")


def read_input() -> Input:
    with open(INPUT_FILE_PATH, "r", encoding="utf-8") as f:
        return [
            list(line.strip())
            for line in f.readlines()
        ]


def is_symbol(s: str) -> bool:
    return not (s.isdigit() or s == EMPTY)


def _count_digits(row: Sequence[str]) -> int:
    assert row[0].isdigit()
    for i, s in enumerate(row[1:], start=1):
        if not s.isdigit():
            return i
    return len(row)


class Solver:
    def __init__(self, input_: Input):
        self.input = np.array(input_)

    def _has_symbol_neighbor(self, r: int, c_start: int, n: int) -> bool:
        rows_to_check = list(filter(lambda r_: 0 <= r_ < self.input.shape[0], [r - 1, r, r + 1]))
        # left bookend
        c_left = c_start - 1
        if c_left >= 0:
            for new_r in rows_to_check:
                if is_symbol(self.input[new_r, c_left]):
                    return True
        # right bookend
        c_right = c_start + n
        if c_right < self.input.shape[1]:
            for new_r in rows_to_check:
                if is_symbol(self.input[new_r, c_right]):
                    return True
        # all along the number
        rows_to_check.remove(r)
        for new_c in range(c_start, c_start + n):
            for new_r in rows_to_check:
                if is_symbol(self.input[new_r, new_c]):
                    return True
        # nothing found
        return False

    def solve(self) -> int:
        data = self.input.copy()
        total = 0
        kept = []
        rejected = []
        for r in range(data.shape[0]):
            for c in range(data.shape[1]):
                s: str = data[r, c]
                if s.isdigit():
                    n_digits = _count_digits(data[r, c:])
                    num = int("".join(data[r, c:c + n_digits]))
                    if self._has_symbol_neighbor(r, c, n_digits):
                        total += num
                        kept.append(num)
                    else:
                        rejected.append(num)
                    data[r, c:c + n_digits] = EMPTY
        return total


def main():
    input_ = read_input()
    solver = Solver(input_)
    answer = solver.solve()
    pprint(answer)


if __name__ == "__main__":
    main()
