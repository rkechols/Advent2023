import math
import re
from pathlib import Path
from pprint import pprint
from typing import Any
import bisect

Input = list[tuple[int, int]]

INPUT_FILE_PATH = Path("input.txt")


def read_input() -> Input:
    with open(INPUT_FILE_PATH, "r", encoding="utf-8") as f:
        times = f.readline()
        distances_to_beat = f.readline()
    times = list(map(int, re.findall(r"\d+", times)))
    distances_to_beat = list(map(int, re.findall(r"\d+", distances_to_beat)))
    return list(zip(times, distances_to_beat))


def _evaluate_race(time_total: int, time_held: int) -> int:
    assert 0 <= time_held <= time_total
    speed = time_held
    time_moving = time_total - time_held
    distance = time_moving * speed
    return distance


def solve(input_: Input) -> int:
    ways = []
    for time_total, distance_to_beat in input_:
        for time_held in range(1, time_total):
            result = _evaluate_race(time_total, time_held)
            if result > distance_to_beat:
                min_hold = time_held
                break
        else:
            ways.append(0)
            continue
        for time_held in range(time_total - 1, 0, -1):
            result = _evaluate_race(time_total, time_held)
            if result > distance_to_beat:
                max_hold = time_held
                break
        else:
            raise RuntimeError(f"{time_total=} | {distance_to_beat=}")
        ways.append(1 + max_hold - min_hold)
    return math.prod(ways)


def main():
    input_ = read_input()
    answer = solve(input_)
    pprint(answer)


if __name__ == "__main__":
    main()
