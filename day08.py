from pathlib import Path
import itertools
import re
from pprint import pprint
from typing import Any

Input = tuple[str, dict[str, tuple[str, str]]]

INPUT_FILE_PATH = Path("input.txt")


def read_input() -> Input:
    graph = {}
    with open(INPUT_FILE_PATH, "r", encoding="utf-8") as f:
        directions = f.readline().strip()
        f.readline()
        for line in f:
            key, left, right = re.fullmatch(r"(\S+) = \(([^,]+), ([^(]+)\)", line.strip()).groups()
            graph[key] = (left, right)
    return directions, graph


def solve(input_: Input) -> int:
    directions, graph = input_
    cur = "AAA"
    target = "ZZZ"
    for i, direction in enumerate(itertools.cycle(directions), start=1):
        left, right = graph[cur]
        match direction:
            case "L":
                cur = left
            case "R":
                cur = right
            case _:
                raise ValueError(f"{i=} {direction=}")
        if cur == target:
            return i


def main():
    input_ = read_input()
    answer = solve(input_)
    pprint(answer)


if __name__ == "__main__":
    main()
