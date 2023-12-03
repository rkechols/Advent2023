from pathlib import Path
from pprint import pprint
import numpy as np

Input = list[tuple[list[int], list[int]]]

INPUT_FILE_PATH = Path("input.txt")


def read_input() -> Input:
    with open(INPUT_FILE_PATH, "r", encoding="utf-8") as f:
        return [
            tuple(map(lambda raw_half: list(map(int, raw_half.split())), line.split(":")[1].split("|")))
            for line in f.readlines()
        ]


def solve1(input_: Input) -> int:
    total = 0
    for winning, yours in input_:
        winning = set(winning)
        count = sum(num in winning for num in yours)
        if count == 0:
            score = 0
        else:
            score = 2 ** (count - 1)
        total += score
    return total


def solve2(input_: Input) -> int:
    n_copies = np.ones(len(input_), dtype=int)
    for i, (winning, yours) in enumerate(input_):
        winning = set(winning)
        count = sum(num in winning for num in yours)
        n_copies[(i + 1):(i + count + 1)] += n_copies[i]
    return n_copies.sum()


def main():
    input_ = read_input()
    answer = solve1(input_)
    pprint(answer)
    answer = solve2(input_)
    pprint(answer)


if __name__ == "__main__":
    main()
