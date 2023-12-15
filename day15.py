from pathlib import Path
from pprint import pprint
from typing import Any

Input = list[str]

INPUT_FILE_PATH = Path("input.txt")


def read_input() -> Input:
    with open(INPUT_FILE_PATH, "r", encoding="utf-8") as f:
        f_data = f.read()
    f_data = f_data.replace("\n", "")
    return [
        s
        for s in f_data.split(",")
        if s != ""
    ]


def hash_alg(s: str) -> int:
    num = 0
    for c in s:
        num += ord(c)
        num *= 17
        num %= 256
    return num


def solve(input_: Input) -> int:
    return sum(map(hash_alg, input_))


def main():
    input_ = read_input()
    answer = solve(input_)
    pprint(answer)


if __name__ == "__main__":
    main()
