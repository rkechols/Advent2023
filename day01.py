from pathlib import Path
import re
from pprint import pprint
from typing import Any

Input = list[str]  # feel free to change per-problem; whatever structure is easiest

INPUT_FILE_PATH = Path("input.txt")


def read_input() -> Input:
    with open(INPUT_FILE_PATH, "r", encoding="utf-8") as f:
        return f.readlines()


def solve(input_: Input) -> Any:
    total = 0
    for line in input_:
        for c in line:
            if c.isdigit():
                first = c
                break
        else:
            raise ValueError(line)
        for c in line[::-1]:
            if c.isdigit():
                last = c
                break
        else:
            raise ValueError(line)
        number = int(f"{first}{last}")
        total += number
    return total


def main():
    input_ = read_input()
    answer = solve(input_)
    pprint(answer)


if __name__ == "__main__":
    main()
