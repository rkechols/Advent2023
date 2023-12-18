import itertools
import re
from enum import Enum
from pathlib import Path
from pprint import pprint
from typing import Self

INPUT_FILE_PATH = Path("input.txt")


class Direction(Enum):
    RIGHT = (1, 0)
    DOWN = (0, -1)
    LEFT = (-1, 0)
    UP = (0, 1)

    @classmethod
    def from_letter(cls, s: str) -> Self:
        if s == "R":
            return cls.RIGHT
        if s == "D":
            return cls.DOWN
        if s == "L":
            return cls.LEFT
        if s == "U":
            return cls.UP
        raise ValueError(s)

    @classmethod
    def from_hex(cls, s: str) -> Self:
        if s == "0":
            return cls.RIGHT
        if s == "1":
            return cls.DOWN
        if s == "2":
            return cls.LEFT
        if s == "3":
            return cls.UP
        raise ValueError(s)

    def shift(self, loc: tuple[int, int], n: int) -> tuple[int, int]:
        shift = tuple(s * n for s in self.value)
        new_loc = tuple(d + s for d, s in zip(loc, shift))
        return new_loc


Input = list[tuple[Direction, int, str]]


def read_input() -> Input:
    data = []
    with open(INPUT_FILE_PATH, "r", encoding="utf-8") as f:
        for line in f:
            # parse line
            match = re.fullmatch(r"([RDLU]) (\d+) \(#([0-9a-f]{6})\)", line.strip())
            direction, num, color = match.groups()
            # reformat and save
            direction = Direction.from_letter(direction)
            num = int(num)
            data.append((direction, num, color))
    return data


def solve(instructions: list[tuple[Direction, int]]) -> int:
    loc = (0, 0)
    vertices = [loc]
    for direction, n in instructions:
        loc = direction.shift(loc, n)
        vertices.append(loc)
    assert loc == (0, 0), "expected a closed loop"
    # calculate area
    sum_of_parallelogram_areas = abs(sum(
        (x1 * y2) - (x2 * y1)  # signed magnitude of the cross-product of the two vectors
        for (x1, y1), (x2, y2) in itertools.pairwise(vertices)
    ))   # guaranteed to be an even integer
    area = sum_of_parallelogram_areas // 2
    # area is calculated as if using center-points of each cell of the array;
    #   we need to pad the area by a margin of 0.5 on all sides
    perimeter = sum(n for _, n in instructions)  # guaranteed to be an even integer
    padding_area = (perimeter // 2) + 1  # +1 is for the corners
    total_area = area + padding_area
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
