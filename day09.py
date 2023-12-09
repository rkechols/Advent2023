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
        stack = [input_row]
        while not np.all((row := stack[-1]) == 0):
            stack.append(row[1:] - row[:-1])
        cur = 0
        for row in reversed(stack):
            cur += row[-1]
        total += cur
    return total


def solve2(input_: Input) -> int:
    total = 0
    for input_row in input_:
        stack = [input_row]
        while not np.all((row := stack[-1]) == 0):
            stack.append(row[1:] - row[:-1])
        cur = 0
        for row in reversed(stack):
            cur = row[0] - cur
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
