from pathlib import Path
import re
import itertools
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

    @classmethod
    def from_hex(cls, s: str) -> Self:
        if s == "3":
            return cls.UP
        if s == "2":
            return cls.LEFT
        if s == "1":
            return cls.DOWN
        if s == "0":
            return cls.RIGHT
        raise ValueError(s)

    def shift(self, loc: tuple[int, int], n: int) -> tuple[int, int]:
        shift = tuple(s * n for s in self.value)
        new_loc = tuple(d + s for d, s in zip(loc, shift))
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


def solve(instructions: list[tuple[Direction, int]]) -> float:
    loc = (0, 0)
    vertices = [loc]
    for direction, n in instructions:
        loc = direction.shift(loc, n)
        vertices.append(loc)
    assert loc == (0, 0), "loop expected"
    # calculate area
    area = abs(sum(
        (x1 * y2) - (x2 * y1)
        for (x1, y1), (x2, y2) in itertools.pairwise(vertices)
    )) // 2  # guaranteed to be even before dividing
    # area is calculated as if using center-points of each cell of the array;
    # we need to pad the area by a margin of 0.5 on all sides
    perimeter = sum(n for _, n in instructions)  # guaranteed to be even
    border_area = (perimeter // 2) + 1  # +1 is for the corners
    total_area = area + border_area
    return total_area


def solve1(input_: Input) -> int:
    instructions = [
        (direction, n)
        for direction, n, _ in input_
    ]
    return solve(instructions)


def hex_to_instruction(hex: str) -> tuple[Direction, int]:
    dist = int(hex[:-1], base=16)
    direction = Direction.from_hex(hex[-1])
    return direction, dist


def solve2(input_: Input) -> int:
    instructions = [
        hex_to_instruction(hex)
        for *_, hex in input_
    ]
    return solve(instructions)


def main():
    input_ = read_input()
    answer = solve1(input_)
    pprint(answer)
    answer = solve2(input_)
    pprint(answer)


if __name__ == "__main__":
    main()
