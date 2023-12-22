from collections import defaultdict
import itertools
from typing import Iterable
import functools
from pathlib import Path
from pprint import pprint

Point = tuple[int, int, int]
Block = tuple[Point, Point]
Input = list[Block]

INPUT_FILE_PATH = Path("input.txt")


def read_input() -> Input:
    with open(INPUT_FILE_PATH, "r", encoding="utf-8") as f:
        return [
            tuple(map(lambda point_raw: tuple(map(int, point_raw.split(","))), line.strip().split("~")))
            for line in f
        ]


def gen_xy_points(block: Block) -> Iterable[tuple[int, int]]:
    p1, p2 = block
    for x in range(min(p1[0], p2[0]), 1 + max(p1[0], p2[0])):
        for y in range(min(p1[1], p2[1]), 1 + max(p1[1], p2[1])):
            yield (x, y)


def gen_xyz_points(block: Block) -> Iterable[tuple[int, int]]:
    p1, p2 = block
    for x in range(min(p1[0], p2[0]), 1 + max(p1[0], p2[0])):
        for y in range(min(p1[1], p2[1]), 1 + max(p1[1], p2[1])):
            for z in range(min(p1[2], p2[2]), 1 + max(p1[2], p2[2])):
                yield (x, y, z)


def solve(blocks: Input) -> int:
    # sort block by z-value, ascending
    blocks = sorted(blocks, key=lambda block: min(p[-1] for p in block))
    # simulate the blocks falling/landing
    xy_highest: dict[tuple[int, int], int] = defaultdict(int)
    blocks_settled = []
    for block in blocks:
        z_min = min(p[-1] for p in block)
        # figure out how far to fall before landing on something
        smallest_z_gap = None
        for x, y in gen_xy_points(block):
            fall_size = z_min - xy_highest[x, y] - 1
            assert fall_size >= 0
            if smallest_z_gap is None or fall_size < smallest_z_gap:
                smallest_z_gap = fall_size
        assert smallest_z_gap is not None
        assert smallest_z_gap >= 0
        # new position of the block after falling
        if smallest_z_gap == 0:
            block_new = block
        else:
            block_new = tuple(
                (x, y, z - smallest_z_gap)
                for x, y, z in block
            )
        blocks_settled.append(block_new)
        z_max = max(p[-1] for p in block_new)
        for xy in gen_xy_points(block_new):
            xy_highest[xy] = z_max
    blocks = blocks_settled
    # register occupied space
    point_to_block_num: dict[Point, int] = {}
    for block_num, block in enumerate(blocks):
        for point in gen_xyz_points(block):
            point_to_block_num[point] = block_num
    # figure out which settled blocks would cause something to fall if removed
    count = 0
    for block_num, block in enumerate(blocks):
        block_nums_above = set()
        for x, y, z in gen_xyz_points(block):
            if (block_num_above := point_to_block_num.get((x, y, z + 1), block_num)) != block_num:
                block_nums_above.add(block_num_above)
        if len(block_nums_above) == 0:
            count += 1
            continue
        for block_num_above in block_nums_above:
            if all(
                point_to_block_num.get((x_up, y_up, z_up - 1), block_num) in (block_num, block_num_above)
                for x_up, y_up, z_up in gen_xyz_points(blocks[block_num_above])
            ):  # all spots below the upper block would be empty upon removal of the block in question
                break
        else:
            count += 1
    return count


def main():
    input_ = read_input()
    answer = solve(input_)
    pprint(answer)


if __name__ == "__main__":
    main()
