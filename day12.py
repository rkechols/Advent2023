import re
from functools import cache
from pathlib import Path
from pprint import pprint

Input = list[tuple[str, tuple[int, ...]]]

INPUT_FILE_PATH = Path("input.txt")

WORKING = "."
BROKEN = "#"
UNK = "?"


def read_input() -> Input:
    with open(INPUT_FILE_PATH, "r", encoding="utf-8") as f:
        to_return = []
        for line in f:
            line = line.strip()
            spring_states, numbers = line.split()
            numbers = tuple(map(int, numbers.split(",")))
            to_return.append((spring_states, numbers))
        return to_return


@cache
def get_regex(numbers: tuple[int, ...]):
    pattern_bookend = "[.?]*"
    pattern_joined_blocks = "[.?]+".join("[#?]{" + str(num) + "}" for num in numbers)
    re_springs = re.compile(pattern_bookend + pattern_joined_blocks + pattern_bookend)
    return re_springs


@cache
def _count_matches(spring_states: str, numbers: tuple[int, ...]) -> int:
    # trim any deterministic prefix
    while len(numbers) > 0:
        next_num = numbers[0]  # what number of BROKEN to try to fit
        # trim the start as long as it must be WORKING (though perhaps marked as UNK)
        while len(spring_states) > 0 and spring_states[0] != BROKEN and (
                (WORKING in spring_states[:next_num])
                or (len(spring_states) >= next_num + 1 and spring_states[next_num] == BROKEN)
        ):
            spring_states = spring_states[1:]
        if len(spring_states) < next_num:  # no space to squeeze in the number
            return 0
        if len(spring_states) == next_num:  # perfect space remaining
            return 0 if (WORKING in spring_states or len(numbers) > 1) else 1
        # at least 1 extra spot
        these_states = spring_states[:next_num]
        next_state = spring_states[next_num]
        if these_states[0] == BROKEN:  # forced fully left
            if WORKING in these_states or next_state == BROKEN:  # invalid
                return 0
            # these_states are all BROKEN or UNK, and next_state is WORKING or UNK;
            # trim off this part
            spring_states = spring_states[(next_num + 1):]
            numbers = numbers[1:]
            continue
        # (WORKING not in these_states) and (next_state != BROKEN);
        # starts with UNK, then has UNK|BROKEN, and next_state is UNK or WORKING
        # alignment unclear
        break

    # base case:
    if len(numbers) == 0:
        return 0 if BROKEN in spring_states else 1
    # find the first UNK still present
    re_springs = get_regex(numbers)
    try:
        i_unk = spring_states.index(UNK)
    except ValueError:  # no more unknowns
        return 0 if re_springs.fullmatch(spring_states) is None else 1
    # try substituting the unk for both options and calculating answers recursively
    prefix = spring_states[:i_unk]
    postfix = spring_states[(i_unk + 1):]
    n_if_working = _count_matches(prefix + WORKING + postfix, numbers)
    n_if_broken = _count_matches(prefix + BROKEN + postfix, numbers)
    return n_if_working + n_if_broken


def solve1(input_: Input) -> int:
    return sum(
        _count_matches(spring_states, numbers)
        for spring_states, numbers in input_
    )


def _count_matches2(spring_sections: list[str], numbers: tuple[int, ...]) -> int:
    n_numbers = len(numbers)
    if n_numbers == 0:
        return 0 if any(BROKEN in sec for sec in spring_sections) else 1
    this_section, *other_sections = spring_sections
    # base case: go straight to brute force
    if len(other_sections) == 0:
        return _count_matches(this_section, numbers)
    # count up how many ways branching from this state, depending how many numbers we put into this section
    total = 0
    # n_numbers == 0:
    if BROKEN not in this_section:  # what if this section uses no numbers?
        total += _count_matches2(other_sections, numbers)
    # n_numbers > 0:
    n_this_section = len(this_section)
    for n_numbers in range(1, n_numbers + 1):
        numbers_sub = numbers[:n_numbers]
        min_len = sum(numbers_sub) + n_numbers - 1
        if min_len > n_this_section:  # can't fit all these numbers into this section
            break
        n_matches_this_section = _count_matches(this_section, numbers_sub)
        if n_matches_this_section == 0:
            continue
        total += n_matches_this_section * _count_matches2(other_sections, numbers[n_numbers:])
    return total


def solve2(input_: Input) -> int:
    total = 0
    for spring_states, numbers in input_:
        # expand
        spring_states = UNK.join(spring_states for _ in range(5))
        numbers = numbers * 5
        # solve
        spring_sections = [
            section
            for section in re.split(rf"[{WORKING}]+", spring_states)
            if section != ""
        ]
        n_matches = _count_matches2(spring_sections, numbers)
        total += n_matches
    return total


def main():
    input_ = read_input()
    answer = solve1(input_)
    pprint(answer)
    # import cProfile
    # profiler = cProfile.Profile()
    # profiler.enable()
    answer = solve2(input_)
    # profiler.disable()
    # profiler.dump_stats("profile.stats")
    pprint(answer)


if __name__ == "__main__":
    main()
