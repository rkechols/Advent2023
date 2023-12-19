from pathlib import Path
import re
from dataclasses import dataclass
from pprint import pprint
from typing import Self

INPUT_FILE_PATH = Path("input.txt")

WORKFLOW_START = "in"
ACCEPT = "A"
REJECT = "R"


@dataclass
class Part:
    x: int
    m: int
    a: int
    s: int

    @classmethod
    def from_str(cls, s: str) -> Self:
        return cls(**eval(f"dict({s})"))

    def total_rating(self) -> int:
        return self.x + self.m + self.a + self.s


@dataclass
class Condition:
    attribute: str
    cond_str: str

    def satisfied_by(self, p: Part) -> bool:
        value = getattr(p, self.attribute)
        return eval(f"{value!r}{self.cond_str}")


Workflow = tuple[list[tuple[Condition, str]], str]


Input = tuple[dict[str, Workflow], list[Part]]


def read_input() -> Input:
    with open(INPUT_FILE_PATH, "r", encoding="utf-8") as f:
        f_data = f.read()
    workflows_raw, parts_raw = f_data.strip().split("\n\n")
    # parse workflows
    workflows = {}
    for workflow_raw in workflows_raw.split("\n"):
        name, steps_raw, default = re.fullmatch(r"(\w+)\{(.+),(\w+)\}", workflow_raw).groups()
        steps = []
        for step_raw in steps_raw.split(","):
            attribute, cond_str, dest = re.fullmatch(r"([xmas])([^:]{2,}):(\w+)", step_raw).groups()
            steps.append((Condition(attribute=attribute, cond_str=cond_str), dest))
        workflows[name] = (steps, default)
    # parse parts
    parts = [
        Part.from_str(part_raw.strip().strip("{}"))
        for part_raw in parts_raw.split("\n")
    ]
    return workflows, parts


def solve(input_: Input) -> int:
    workflows, parts = input_
    total = 0
    for part in parts:
        workflow_name = WORKFLOW_START
        while workflow_name not in (ACCEPT, REJECT):
            rules, default = workflows[workflow_name]
            for condition, dest in rules:
                if condition.satisfied_by(part):
                    workflow_name = dest
                    break
            else:
                workflow_name = default
        if workflow_name == ACCEPT:
            total += part.total_rating()
        # if REJECT: don't add it to the total
    return total


def main():
    input_ = read_input()
    answer = solve(input_)
    pprint(answer)


if __name__ == "__main__":
    main()
