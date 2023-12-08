from pathlib import Path
import itertools
import re
from pprint import pprint
from typing import Any, Literal

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


def _apply_direction(cur: str, direction: Literal["L", "R"], graph: dict[str, tuple[str, str]]) -> str:
    left, right = graph[cur]
    match direction:
        case "L":
            return left
        case "R":
            return right
        case _:
            raise ValueError(f"{cur=} | {direction=}")


def solve1(input_: Input) -> int:
    directions, graph = input_
    cur = "AAA"
    target = "ZZZ"
    for i, direction in enumerate(itertools.cycle(directions), start=1):
        cur = _apply_direction(cur, direction, graph)
        if cur == target:
            return i


def solve2(input_: Input) -> int:
    directions, graph = input_
    curs = {loc for loc in graph if loc.endswith("A")}
    for i, direction in enumerate(itertools.cycle(directions), start=1):
        curs = {
            _apply_direction(cur, direction, graph)
            for cur in curs
        }
        if all(cur.endswith("Z") for cur in curs):
            return i


def main():
    input_ = read_input()
    answer = solve1(input_)
    pprint(answer)
    answer = solve2(input_)
    pprint(answer)


if __name__ == "__main__":
    main()
