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
    range_transforms: list[RangeTransform]


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
        range_transforms = [
            RangeTransform(*map(int, line.split()))
            for line in lines[1:]
            if line.strip() != ""
        ]
        maps.append(Map(name=name, range_transforms=range_transforms))
    return Input(seeds=seeds, maps=maps)


def solve1(input_: Input) -> int:
    current_nums = set(input_.seeds)
    for map_ in input_.maps:
        new_nums = set()
        for r in map_.range_transforms:
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
        new_nums.update(current_nums)
        current_nums = new_nums
    return min(current_nums)


Section = tuple[int, int]  # tuple of form (start, end) where BOTH values are INCLUSIVE


def _simplify_sections(sections: list[Section]) -> list[Section]:
    i = 0
    while i + 1 < len(sections):
        (low_start, low_end), (high_start, high_end) = sections[i:(i + 2)]
        assert low_start <= high_start
        if low_end + 1 >= high_start:
            mashed_section = (min(low_start, high_start), max(low_end, high_end))
            sections = sections[:i] + [mashed_section] + sections[(i + 2):]
        else:
            i += 1
    return sections


def _range_overlap(sec_query: Section, sec_key: Section) -> tuple[Optional[Section], list[Section]]:
    sq_low, sq_high = sec_query
    assert sq_low <= sq_high
    sk_low, sk_high = sec_key
    assert sk_low <= sk_high
    # disjoint sections
    if sq_high < sk_low or sk_high < sq_low:
        return None, [sec_query]
    # overlapping sections
    # fudge things to avoid boundaries perfectly overlapping
    if sq_low == sk_low:
        sk_low -= 1
    if sq_high == sk_high:
        sk_high += 1
    # figure out the actual overlap
    if sq_low < sk_low <= sq_high < sk_high:
        return (sk_low, sq_high), [(sq_low, sk_low - 1)]
    elif sq_low < sk_low <= sk_high < sq_high:
        return (sk_low, sk_high), [(sq_low, sk_low - 1), (sk_high + 1, sq_high)]
    elif sk_low < sq_low <= sq_high < sk_high:
        return (sq_low, sq_high), []
    elif sk_low < sq_low <= sk_high < sq_high:
        return (sq_low, sk_high), [(sk_high + 1, sq_high)]
    else:
        raise ValueError(f"{(sq_low, sq_high)=}, {(sk_low, sk_high)=}")


def solve2(input_: Input) -> int:
    input_sections = _simplify_sections(sorted(
        (start, start + n - 1)
        for start, n in zip(input_.seeds[::2], input_.seeds[1::2])
    ))
    for map_ in input_.maps:
        output_sections = []
        for r in map_.range_transforms:
            transforming_sec = (r.start_in, r.start_in + r.n - 1)
            shift = r.start_out - r.start_in
            i = 0
            while i < len(input_sections):
                input_sec = input_sections[i]
                overlap, leftovers = _range_overlap(input_sec, transforming_sec)
                if overlap is not None:
                    overlap_shifted = (overlap[0] + shift, overlap[1] + shift)
                    bisect.insort(output_sections, overlap_shifted)
                    input_sections = input_sections[:i] + leftovers + input_sections[(i + 1):]
                else:
                    i += 1
            if len(input_sections) == 0:
                break
        for input_sec in input_sections:  # sections that go unchanged
            bisect.insort(output_sections, input_sec)
        input_sections = _simplify_sections(output_sections)
    return min(low for low, _ in input_sections)


def main():
    input_ = read_input()
    answer = solve1(input_)
    pprint(answer)
    answer = solve2(input_)
    pprint(answer)


if __name__ == "__main__":
    main()
