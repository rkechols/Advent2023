from pathlib import Path
from collections import defaultdict
import re
from pprint import pprint
from typing import Any

Input = dict[int, list[dict[str, int]]]

INPUT_FILE_PATH = Path("input.txt")

COLOR_MAXES = {
    "red": 12,
    "green": 13,
    "blue": 14,
}


def read_input() -> Input:
    data = {}
    with open(INPUT_FILE_PATH, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line == "":
                continue
            match = re.match(r"Game (\d+):", line)
            game_num = int(match.group(1))
            pulls_raw = line[match.end():].split(";")
            pulls = []
            for pull in pulls_raw:
                counts = defaultdict(int)
                for color in COLOR_MAXES.keys():
                    if (match := re.search(f"(\\d+) {color}", pull)) is not None:
                        counts[color] = int(match.group(1))
                pulls.append(counts)
            data[game_num] = pulls
    return data


def solve(input_: Input) -> Any:
    good_game_nums = set()
    for game_num, pulls in input_.items():
        if all(
            all(pull[color] <= count_max for color, count_max in COLOR_MAXES.items())
            for pull in pulls
        ):
            good_game_nums.add(game_num)
    return sum(good_game_nums)


def main():
    input_ = read_input()
    answer = solve(input_)
    pprint(answer)


if __name__ == "__main__":
    main()
