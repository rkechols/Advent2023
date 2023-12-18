from pathlib import Path
import numpy as np
import re
from pprint import pprint
from typing import Self
from enum import Enum


class Direction(Enum):
    UP = (-1, 0)
    LEFT = (0, -1)
    DOWN = (1, 0)
    RIGHT = (0, 1)

    @classmethod
    def from_letter(cls, s: str) -> Self:
        if s == "U":
            return cls.UP
        if s == "L":
            return cls.LEFT
        if s == "D":
            return cls.DOWN
        if s == "R":
            return cls.RIGHT
        raise ValueError(s)

    def shift(self, loc: tuple[int, int]) -> tuple[int, int]:
        new_loc = tuple(d + s for d, s in zip(loc, self.value))
        return new_loc

Input = list[tuple[Direction, int, str]]

INPUT_FILE_PATH = Path("input.txt")


def read_input() -> Input:
    data = []
    with open(INPUT_FILE_PATH, "r", encoding="utf-8") as f:
        for line in f:
            # parse line
            match = re.fullmatch(r"([RULD]) (\d+) \(#([0-9a-f]{6})\)", line.strip())
            direction, num, color = match.groups()
            # reformat and save
            direction = Direction.from_letter(direction)
            num = int(num)
            data.append((direction, num, color))
    return data


def solve(input_: Input) -> int:
    dug = set()
    loc = (0, 0)
    for direction, n, color in input_:
        for _ in range(n):
            loc = direction.shift(loc)
            dug.add(loc)
    assert loc == (0, 0), "loop expected"
    # figure out bounds
    dug_np = np.array(list(dug))
    top, bottom = dug_np[:, 0].min(), dug_np[:, 0].max()
    left, right = dug_np[:, 1].min(), dug_np[:, 1].max()
    # try finding all cells internal to the dig loop
    internal = set()
    external = set()
    for loc in dug:
        for direction in Direction:
            search_start = direction.shift(loc)
            if any(search_start in set_known for set_known in (dug, internal, external)):
                continue
            to_search = {search_start}
            searched = set()
            went_out_of_bounds = False
            while len(to_search) > 0:
                loc_searching = to_search.pop()
                searched.add(loc_searching)
                if not (top <= loc_searching[0] <= bottom and left <= loc_searching[1] <= right):
                    # condsidered "out of bounds"; this search is certainly not bounded by the dig loop
                    went_out_of_bounds = True
                    searched.update(to_search)
                    break
                for search_direction in Direction:
                    new_loc_searching = search_direction.shift(loc_searching)
                    if any(new_loc_searching in set_dont_search for set_dont_search in (dug, searched, to_search)):
                        continue
                    to_search.add(new_loc_searching)
            if went_out_of_bounds:
                external.update(searched)
            else:
                internal.update(searched)
    all_dug = dug | internal
    return len(all_dug)


def main():
    input_ = read_input()
    answer = solve(input_)
    pprint(answer)


if __name__ == "__main__":
    main()
