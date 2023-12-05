import copy
from pathlib import Path
import re
from pprint import pprint
from typing import Any

Input = tuple[
    list[int],
    list[tuple[
        str,
        list[tuple[int, int, int]],
    ]],
]

INPUT_FILE_PATH = Path("input.txt")


def read_input() -> Input:
    with open(INPUT_FILE_PATH, "r", encoding="utf-8") as f:
        f_content = f.read()
    sections = re.split(r"\n\n", f_content)
    seeds = list(map(int, sections[0].split(":")[1].split()))
    maps = []
    for section in sections[1:]:
        lines = section.split("\n")
        name = lines[0].strip()
        ranges = [
            tuple(map(int, line.split()))
            for line in lines[1:]
            if line.strip()
        ]
        maps.append((name, ranges))
    return seeds, maps


def solve(input_: Input) -> int:
    seeds, maps = input_
    current_nums = set(seeds)
    for _, map_ in maps:
        new_nums = set()
        for start_out, start_in, n in map_:
            range_in = range(start_in, start_in + n)
            shift = start_out - start_in
            to_discard = set()
            for num in current_nums:
                if num in range_in:
                    new_nums.add(num + shift)
                    to_discard.add(num)
            current_nums -= to_discard
            if len(current_nums) == 0:
                break
        for num_no_match in current_nums:
            new_nums.add(num_no_match)
        current_nums = new_nums
    return min(current_nums)


def main():
    input_ = read_input()
    answer = solve(input_)
    pprint(answer)


if __name__ == "__main__":
    main()
