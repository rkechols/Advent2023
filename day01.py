from pathlib import Path
import re
from pprint import pprint
from typing import Any

Input = list[str]  # feel free to change per-problem; whatever structure is easiest

INPUT_FILE_PATH = Path("input.txt")


def read_input() -> Input:
    with open(INPUT_FILE_PATH, "r", encoding="utf-8") as f:
        return f.readlines()


def solve1(input_: Input) -> Any:
    total = 0
    for line in input_:
        for c in line:
            if c.isdigit():
                first = c
                break
        else:
            raise ValueError(line)
        for c in line[::-1]:
            if c.isdigit():
                last = c
                break
        else:
            raise ValueError(line)
        number = int(f"{first}{last}")
        total += number
    return total


def to_digit(num: str) -> str:
    if num.isdigit():
        return num
    match num:
        case "one":
            return "1"
        case "two":
            return "2"
        case "three":
            return "3"
        case "four":
            return "4"
        case "five":
            return "5"
        case "six":
            return "6"
        case "seven":
            return "7"
        case "eight":
            return "8"
        case "nine":
            return "9"
        case _:
            raise ValueError(num)


def solve2(input_: Input) -> Any:
    total = 0
    for line in input_:
        first = re.search(r"\d|one|two|three|four|five|six|seven|eight|nine", line).group(0)
        last = re.search(r"\d|enin|thgie|neves|xis|evif|ruof|eerht|owt|eno", line[::-1]).group(0)[::-1]
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
