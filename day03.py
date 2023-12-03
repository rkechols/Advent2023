from pathlib import Path
from pprint import pprint
from typing import Sequence

import numpy as np

EMPTY = "."
GEAR = "*"

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

    def solve1(self) -> int:
        data = self.input.copy()
        total = 0
        for r in range(data.shape[0]):
            for c in range(data.shape[1]):
                if data[r, c].isdigit():
                    n_digits = _count_digits(data[r, c:])
                    if self._has_symbol_neighbor(r, c, n_digits):
                        num = int("".join(data[r, c:c + n_digits]))
                        total += num
                    data[r, c:c + n_digits] = EMPTY
        return total

    def _collect_adjacent_numbers(self, r: int, c: int) -> list[int]:
        data = self.input.copy()
        adjacent_numbers = []
        for r_shift in (-1, 0, 1):
            new_r = r + r_shift
            for c_shift in (-1, 0, 1):  # order is important
                if r_shift == 0 and c_shift == 0:
                    continue
                new_c = c + c_shift
                if data[new_r, new_c].isdigit():
                    c_start = new_c
                    while c_start > 0 and data[new_r, c_start - 1].isdigit():
                        c_start -= 1
                    n_digits = _count_digits(data[new_r, c_start:])
                    num = int("".join(data[new_r, c_start:c_start + n_digits]))
                    adjacent_numbers.append(num)
                    data[new_r, c_start:c_start + n_digits] = EMPTY
        return adjacent_numbers

    def solve2(self) -> int:
        total = 0
        for r in range(self.input.shape[0]):
            for c in range(self.input.shape[1]):
                if self.input[r, c] == GEAR:
                    adjacent_numbers = self._collect_adjacent_numbers(r, c)
                    if len(adjacent_numbers) == 2:
                        gear_ratio = adjacent_numbers[0] * adjacent_numbers[1]
                        total += gear_ratio
        return total


def main():
    input_ = read_input()
    solver = Solver(input_)
    answer = solver.solve1()
    pprint(answer)
    answer = solver.solve2()
    pprint(answer)


if __name__ == "__main__":
    main()
