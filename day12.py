from pathlib import Path
import re
from collections import Counter
from pprint import pprint

Input = list[tuple[str, list[int]]]

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
            numbers = list(map(int, numbers.split(",")))
            to_return.append((spring_states, numbers))
        return to_return


def _count_matches(spring_states: str, re_springs: re.Pattern) -> int:
    try:
        i_unk = spring_states.index(UNK)
    except ValueError:  # no more unknowns
        return 0 if re_springs.fullmatch(spring_states) is None else 1
    # try substituting the unk for both options and calculating answers recursively
    prefix = spring_states[:i_unk]
    postfix = spring_states[(i_unk + 1):]
    n_if_working = _count_matches(prefix + WORKING + postfix, re_springs)
    n_if_broken = _count_matches(prefix + BROKEN + postfix, re_springs)
    return n_if_working + n_if_broken


def solve(input_: Input) -> int:
    total = 0
    for spring_states, numbers in input_:
        pattern_bookend = "[.?]*"
        pattern_joined_blocks = "[.?]+".join("[#?]{" + str(num) + "}" for num in numbers)
        re_springs = re.compile(pattern_bookend + pattern_joined_blocks + pattern_bookend)
        n_matches = _count_matches(spring_states, re_springs)
        total += n_matches
    return total


def main():
    input_ = read_input()
    answer = solve(input_)
    pprint(answer)


if __name__ == "__main__":
    main()
