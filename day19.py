import dataclasses
import math
import re
from collections import defaultdict
from enum import Enum
from pathlib import Path
from pprint import pprint
from typing import Self

INPUT_FILE_PATH = Path("input.txt")

WORKFLOW_START = "in"
ACCEPT = "A"
REJECT = "R"


@dataclasses.dataclass(frozen=True)
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


class CondOperator(Enum):
    LT = "<"
    GT = ">"

    def eval(self, left: int, right: int) -> bool:
        if self == self.LT:
            return left < right
        elif self == self.GT:
            return left > right
        else:
            raise ValueError(self)


@dataclasses.dataclass
class Condition:
    attribute: str
    cond_op: CondOperator
    cond_val: int

    def satisfied_by(self, value: int) -> bool:
        return self.cond_op.eval(value, self.cond_val)


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
            attribute, cond_op, cond_val, dest = re.fullmatch(r"([xmas])([<>])(\d+):(\w+)", step_raw).groups()
            steps.append((
                Condition(attribute=attribute, cond_op=CondOperator(cond_op), cond_val=int(cond_val)),
                dest,
            ))
        workflows[name] = (steps, default)
    # parse parts
    parts = [
        Part.from_str(part_raw.strip().strip("{}"))
        for part_raw in parts_raw.split("\n")
    ]
    return workflows, parts


def solve1(input_: Input) -> int:
    workflows, parts = input_
    total = 0
    for part in parts:
        workflow_name = WORKFLOW_START
        while workflow_name not in (ACCEPT, REJECT):
            rules, default = workflows[workflow_name]
            for condition, dest in rules:
                if condition.satisfied_by(getattr(part, condition.attribute)):
                    workflow_name = dest
                    break
            else:
                workflow_name = default
        if workflow_name == ACCEPT:
            total += part.total_rating()
        # if REJECT: don't add it to the total
    return total


Range = tuple[int, int]  # inclusive on both ends

ATTRIBUTE_START_RANGE: Range = (1, 4000)


@dataclasses.dataclass(frozen=True)
class PartRange:
    x: Range
    m: Range
    a: Range
    s: Range

    def split(self, condition: Condition) -> tuple[Self | None, Self | None]:
        relevant_range: Range = getattr(self, condition.attribute)
        n_bounds_in_condition = sum(
            condition.satisfied_by(bound)
            for bound in relevant_range
        )
        if n_bounds_in_condition == 0:  # no overlap
            return None, self
        elif n_bounds_in_condition == 1:  # partial overlap
            low, high = relevant_range
            if condition.cond_op == CondOperator.LT:
                new_range_in = (low, condition.cond_val - 1)
                new_range_out = (condition.cond_val, high)
            elif condition.cond_op == CondOperator.GT:
                new_range_out = (low, condition.cond_val)
                new_range_in = (condition.cond_val + 1, high)
            else:
                raise ValueError(condition.cond_op)
            part_range_in = dataclasses.replace(self, **{condition.attribute: new_range_in})
            part_range_out = dataclasses.replace(self, **{condition.attribute: new_range_out})
            return part_range_in, part_range_out
        elif n_bounds_in_condition == 2:  # total overlap
            return self, None
        else:
            raise ValueError(f"{n_bounds_in_condition=}")

    def count(self) -> int:
        return math.prod(
            1 + high - low
            for low, high in (self.x, self.m, self.a, self.s)
        )


def solve2(workflows: dict[str, Workflow]) -> int:
    workflow_ranges: dict[str, set[PartRange]] = defaultdict(set)
    workflow_ranges[WORKFLOW_START].add(PartRange(
        x=ATTRIBUTE_START_RANGE,
        m=ATTRIBUTE_START_RANGE,
        a=ATTRIBUTE_START_RANGE,
        s=ATTRIBUTE_START_RANGE,
    ))
    accepted: set[PartRange] = set()
    while len(workflow_ranges) > 0:
        workflow_name, ranges = workflow_ranges.popitem()
        rules, default = workflows[workflow_name]
        resolved: dict[str, set[PartRange]] = defaultdict(set)
        for part_range in ranges:
            range_leftover = part_range
            for condition, dest in rules:
                range_match, range_leftover = range_leftover.split(condition)
                if range_match is not None:
                    resolved[dest].add(range_match)
                if range_leftover is None:
                    break
            else:  # ran out of rules, but range_leftover is still not None
                resolved[default].add(range_leftover)
        for dest, new_part_ranges in resolved.items():
            if dest == ACCEPT:
                accepted.update(new_part_ranges)
            elif dest == REJECT:
                continue  # discard
            else:
                workflow_ranges[dest].update(new_part_ranges)
    # total it up
    return sum(
        part_range.count()
        for part_range in accepted
    )


def main():
    input_ = read_input()
    answer = solve1(input_)
    pprint(answer)
    answer = solve2(input_[0])
    pprint(answer)


if __name__ == "__main__":
    main()
