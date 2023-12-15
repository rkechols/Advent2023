import re
from collections import defaultdict, OrderedDict
from pathlib import Path
from pprint import pprint

Input = list[str]

INPUT_FILE_PATH = Path("input.txt")


def read_input() -> Input:
    with open(INPUT_FILE_PATH, "r", encoding="utf-8") as f:
        f_data = f.read()
    f_data = f_data.replace("\n", "")
    return [
        s
        for s in f_data.split(",")
        if s != ""
    ]


def hash_alg(s: str) -> int:
    num = 0
    for c in s:
        num += ord(c)
        num *= 17
        num %= 256
    return num


def solve1(input_: Input) -> int:
    return sum(map(hash_alg, input_))


def solve2(input_: Input) -> int:
    boxes = defaultdict(OrderedDict)
    for line in input_:
        label, op = re.fullmatch(r"([a-zA-Z]+)(-|=\d)", line).groups()
        box_num = hash_alg(label)
        box: OrderedDict = boxes[box_num]
        try:
            num_previous = box[label]
        except KeyError:
            num_previous = None
        if op == "-":
            if num_previous is not None:
                del box[label]
        elif op.startswith("="):
            num = int(op[1:])
            box[label] = num
        else:
            raise ValueError(op)
    focus_power = 0
    for box_num in range(256):
        for lens_index, num in enumerate(boxes[box_num].values(), start=1):
            focus_power += (box_num + 1) * lens_index * num
    return focus_power


def main():
    input_ = read_input()
    answer = solve1(input_)
    pprint(answer)
    answer = solve2(input_)
    pprint(answer)


if __name__ == "__main__":
    main()
