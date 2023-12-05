import bisect
import re
from pathlib import Path
from pprint import pprint
from typing import NamedTuple, Optional
from dataclasses import dataclass

INPUT_FILE_PATH = Path("input.txt")


RangeTransform = NamedTuple("RangeTransform", [
    ("start_out", int),
    ("start_in", int),
    ("n", int),
])


@dataclass
class Map:
    name: str
    ranges: list[RangeTransform]


@dataclass
class Input:
    seeds: list[int]
    maps: list[Map]


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
            RangeTransform(*map(int, line.split()))
            for line in lines[1:]
            if line.strip()
        ]
        maps.append(Map(name=name, ranges=ranges))
    return Input(seeds=seeds, maps=maps)


def solve1(input_: Input) -> int:
    current_nums = set(input_.seeds)
    for map_ in input_.maps:
        new_nums = set()
        for r in map_.ranges:
            range_in = range(r.start_in, r.start_in + r.n)
            shift = r.start_out - r.start_in
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


def _simplify_ranges(ranges: list[tuple[int, int]]) -> list[tuple[int, int]]:
    i = 0
    while i + 1 < len(ranges):
        (low_start, low_end), (high_start, high_end) = ranges[i:(i + 2)]
        assert low_start <= high_start
        if low_end + 1 >= high_start:
            mashed_range = (min(low_start, high_start), max(low_end, high_end))
            ranges = ranges[:i] + [mashed_range] + ranges[(i + 2):]
        else:
            i += 1
    return ranges


def _range_overlap(r_query: tuple[int, int], r_key: tuple[int, int]) -> tuple[
    Optional[tuple[int, int]],
    list[tuple[int, int]],
]:
    rq_low, rq_high = r_query
    assert rq_low <= rq_high
    rk_low, rk_high = r_key
    assert rk_low <= rk_high
    # disjoint ranges
    if rq_high < rk_low or rk_high < rq_low:
        return None, [r_query]
    # overlapping ranges
    # fudge things to avoid boundaries perfectly overlapping
    if rq_low == rk_low:
        rk_low -= 1
    if rq_high == rk_high:
        rk_high += 1
    # figure out the actual overlap
    if rq_low < rk_low <= rq_high < rk_high:
        return (rk_low, rq_high), [(rq_low, rk_low - 1)]
    elif rq_low < rk_low <= rk_high < rq_high:
        return (rk_low, rk_high), [(rq_low, rk_low - 1), (rk_high + 1, rq_high)]
    elif rk_low < rq_low <= rq_high < rk_high:
        return (rq_low, rq_high), []
    elif rk_low < rq_low <= rk_high < rq_high:
        return (rq_low, rk_high), [(rk_high + 1, rq_high)]
    else:
        raise ValueError(f"{(rq_low, rq_high)=}, {(rk_low, rk_high)=}")


def solve2(input_: Input) -> int:
    input_ranges = _simplify_ranges(sorted(
        (start, start + n - 1)
        for start, n in zip(input_.seeds[::2], input_.seeds[1::2])
    ))
    for map_ in input_.maps:
        output_ranges = []
        for r in map_.ranges:
            transform_range = (r.start_in, r.start_in + r.n - 1)
            shift = r.start_out - r.start_in
            i = 0
            while i < len(input_ranges):
                input_range = input_ranges[i]
                overlap, leftovers = _range_overlap(input_range, transform_range)
                if overlap is not None:
                    overlap_shifted = (overlap[0] + shift, overlap[1] + shift)
                    bisect.insort(output_ranges, overlap_shifted)
                    input_ranges = input_ranges[:i] + leftovers + input_ranges[(i + 1):]
                else:
                    i += 1
            if len(input_ranges) == 0:
                break
        for input_range in input_ranges:  # ranges that go unchanged
            bisect.insort(output_ranges, input_range)
        input_ranges = _simplify_ranges(output_ranges)
    return min(low for low, _ in input_ranges)


def main():
    input_ = read_input()
    answer = solve1(input_)
    pprint(answer)
    answer = solve2(input_)
    pprint(answer)


if __name__ == "__main__":
    main()
