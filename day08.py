import itertools
import re
from pathlib import Path
from pprint import pprint
from typing import Literal

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


def _map_path_to_bools(path: list[str]) -> list[bool]:
    return [
        loc.endswith("Z")
        for loc in path
    ]


def solve2(input_: Input) -> int:
    directions, graph = input_
    assert len(directions) > 0
    cycles = {}
    for start in graph.keys():
        if not start.endswith("A"):
            continue  # not a starter
        path = [start]
        cur = start
        for direction in itertools.cycle(directions):
            cur = _apply_direction(cur, direction, graph)
            try:
                loop_start = path.index(cur)
            except ValueError:
                path.append(cur)
            else:
                break
        else:
            raise ValueError("empty list of directions")
        intro, cycle = path[:loop_start], path[loop_start:]
        cycles[start] = (intro, cycle)
    pprint(cycles)
    cycles_bools = {
        start: (_map_path_to_bools(intro), _map_path_to_bools(cycle))
        for start, (intro, cycle) in cycles.items()
    }
    pprint(cycles_bools)
    has_z = {
        start: (any(intro), any(cycle))
        for start, (intro, cycle) in cycles_bools.items()
    }
    pprint(has_z)
    for start, (intro, cycle) in cycles_bools.items():
        if not any(itertools.chain(intro, cycle)):
            raise ValueError(f"cycle starting from {start} did not have any True value")
    print("😖")


def main():
    input_ = read_input()
    answer = solve1(input_)
    pprint(answer)
    answer = solve2(input_)
    pprint(answer)


if __name__ == "__main__":
    main()
