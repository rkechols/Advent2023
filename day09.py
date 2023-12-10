from pathlib import Path
from pprint import pprint

import numpy as np

Input = list[np.ndarray]

INPUT_FILE_PATH = Path("input.txt")


def read_input() -> Input:
    with open(INPUT_FILE_PATH, "r", encoding="utf-8") as f:
        return [
            np.array(
                list(map(int, line.strip().split())),
                dtype=int,
            )
            for line in f
        ]


def solve1(input_: Input) -> int:
    total = 0
    for input_row in input_:
        row = input_row
        stack_lasts = [row[-1]]
        while not np.all(row == 0):
            row = row[1:] - row[:-1]
            stack_lasts.append(row[-1])
        cur = 0
        for row_last in reversed(stack_lasts):
            cur += row_last
        total += cur
    return total


def solve2(input_: Input) -> int:
    total = 0
    for input_row in input_:
        row_first = input_row
        stack_firsts = [row_first[0]]
        while not np.all(row_first == 0):
            row_first = row_first[1:] - row_first[:-1]
            stack_firsts.append(row_first[0])
        cur = 0
        for row_first in reversed(stack_firsts):
            cur = row_first - cur
        total += cur
    return total


def main():
    input_ = read_input()
    answer = solve1(input_)
    pprint(answer)
    answer = solve2(input_)
    pprint(answer)


if __name__ == "__main__":
    main()
