import re
from pathlib import Path
from pprint import pprint

Input = list[str]

INPUT_FILE_PATH = Path("input.txt")


def read_input() -> Input:
    with open(INPUT_FILE_PATH, "r", encoding="utf-8") as f:
        return [
            line_
            for line in f
            if (line_ := line.strip()) != ""
        ]


def solve1(input_: Input) -> int:
    total = 0
    for line in input_:
        first = re.search(r"\d", line).group(0)
        last = re.search(r"\d", line[::-1]).group(0)
        number = int(f"{first}{last}")
        total += number
    return total


DIGITS_BY_NAME = {
    "one": "1",
    "two": "2",
    "three": "3",
    "four": "4",
    "five": "5",
    "six": "6",
    "seven": "7",
    "eight": "8",
    "nine": "9",
}


def to_digit(num: str) -> str:
    if num.isdigit():
        return num
    return DIGITS_BY_NAME[num]


def solve2(input_: Input) -> int:
    union_digit_names = "|".join(DIGITS_BY_NAME.keys())
    re_digits_forward = re.compile(f"\\d|{union_digit_names}")
    re_digits_backward = re.compile(f"\\d|{union_digit_names[::-1]}")
    total = 0
    for line in input_:
        first = re_digits_forward.search(line).group(0)
        last = re_digits_backward.search(line[::-1]).group(0)[::-1]
        number = int(f"{to_digit(first)}{to_digit(last)}")
        total += number
    return total


def main():
    input_ = read_input()
    answer = solve1(input_)
    pprint(answer)
    answer = solve2(input_)
    pprint(answer)


if __name__ == "__main__":
    main()
