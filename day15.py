import re
from collections import defaultdict, OrderedDict
from pathlib import Path
from pprint import pprint

Input = list[str]

INPUT_FILE_PATH = Path("input.txt")

N_BOXES = 256


def read_input() -> Input:
    with open(INPUT_FILE_PATH, "r", encoding="utf-8") as f:
        f_data = f.read()
    f_data = f_data.replace("\n", "").strip()
    return list(f_data.split(","))


def hash_alg(s: str) -> int:
    num = 0
    for c in s:
        num += ord(c)
        num *= 17
        num %= N_BOXES
    return num


def solve1(input_: Input) -> int:
    return sum(map(hash_alg, input_))


def solve2(input_: Input) -> int:
    boxes = defaultdict(OrderedDict)
    for instruction in input_:
        label, op = re.fullmatch(r"([a-zA-Z]+)(-|=\d)", instruction).groups()
        box_num = hash_alg(label)
        box = boxes[box_num]
        if op == "-":
            if label in box:
                del box[label]
        elif op.startswith("="):
            box[label] = int(op.removeprefix("="))
        else:
            raise ValueError(f"{op=}")
    focus_power = sum(
        (box_num + 1) * lens_index * num
        for box_num in range(N_BOXES)
        for lens_index, num in enumerate(boxes[box_num].values(), start=1)
    )
    return focus_power


def main():
    input_ = read_input()
    answer = solve1(input_)
    pprint(answer)
    answer = solve2(input_)
    pprint(answer)


if __name__ == "__main__":
    main()
