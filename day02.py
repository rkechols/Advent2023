import math
import re
from collections import defaultdict
from pathlib import Path
from pprint import pprint

Input = dict[int, list[tuple[str, int]]]

INPUT_FILE_PATH = Path("input.txt")

COLOR_MAXES = {
    "red": 12,
    "green": 13,
    "blue": 14,
}
COLORS = set(COLOR_MAXES.keys())

RE_COLOR_COUNT = re.compile(fr"(\d+)\s+({'|'.join(COLORS)})")


def read_input() -> Input:
    data = {}
    with open(INPUT_FILE_PATH, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line == "":
                continue
            match = re.match(r"Game (\d+):", line)
            game_num = int(match.group(1))
            pulls = re.split("[,;]", line[match.end():])
            pulls = [
                (match.group(2), int(match.group(1)))
                for pull in pulls
                if (match := RE_COLOR_COUNT.search(pull)) is not None
            ]
            data[game_num] = pulls
    return data


def solve1(input_: Input) -> int:
    return sum(
        game_num
        for game_num, pulls in input_.items()
        if all(
            count <= COLOR_MAXES[color]
            for color, count in pulls
        )
    )


def solve2(input_: Input) -> int:
    total_power = 0
    for pulls in input_.values():
        biggest_seen = defaultdict(int)
        for color, count in pulls:
            best_prev = biggest_seen[color]
            biggest_seen[color] = max(best_prev, count)
        power = math.prod((biggest_seen[color] for color in COLORS))
        total_power += power
    return total_power


def main():
    input_ = read_input()
    answer = solve1(input_)
    pprint(answer)
    answer = solve2(input_)
    pprint(answer)


if __name__ == "__main__":
    main()
