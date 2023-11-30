from pathlib import Path
from pprint import pprint
from typing import Any

Input = str  # feel free to change per-problem; whatever structure is easiest

INPUT_FILE_PATH = Path("input.txt")


def read_input() -> Input:
    with open(INPUT_FILE_PATH, "r", encoding="utf-8") as f:
        return f.read()


def solve(input_: Input) -> Any:
    pass


def main():
    input_ = read_input()
    answer = solve(input_)
    pprint(answer)


if __name__ == "__main__":
    main()
