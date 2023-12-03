from pathlib import Path
from pprint import pprint
from typing import Any

Input = list[tuple[list[int], list[int]]]

INPUT_FILE_PATH = Path("input.txt")


def read_input() -> Input:
    with open(INPUT_FILE_PATH, "r", encoding="utf-8") as f:
        return [
            tuple(map(lambda raw_half: list(map(int, raw_half.split())), line.split(":")[1].split("|")))
            for line in f.readlines()
        ]


def solve(input_: Input) -> int:
    total = 0
    for winning, yours in input_:
        winning = set(winning)
        count = 0
        for num in yours:
            if num in winning:
                count += 1
        if count == 0:
            score = 0
        else:
            score = 2 ** (count - 1)
        total += score
    return total


def main():
    input_ = read_input()
    answer = solve(input_)
    pprint(answer)


if __name__ == "__main__":
    main()
