import itertools
import math
import re
from pathlib import Path
from pprint import pprint

Input = tuple[str, dict[str, tuple[str, str]]]

INPUT_FILE_PATH = Path("input.txt")


def read_input() -> Input:
    with open(INPUT_FILE_PATH, "r", encoding="utf-8") as f:
        directions = f.readline().strip()
        f.readline()
        graph = {
            match.group(1): (match.group(2), match.group(3))
            for line in f
            if (match := re.fullmatch(r"(.+) = \((.+), (.+)\)", line.strip())) is not None
        }
    return directions, graph


def _apply_direction(cur: str, direction: str, graph: dict[str, tuple[str, str]]) -> str:
    left, right = graph[cur]
    match direction:
        case "L":
            return left
        case "R":
            return right
        case _:
            raise ValueError(f"{cur=} | {direction=}")


def solve1(input_: Input) -> int:
    directions, graph = input_
    cur = "AAA"
    target = "ZZZ"
    for i, direction in enumerate(itertools.cycle(directions), start=1):
        cur = _apply_direction(cur, direction, graph)
        if cur == target:
            return i


def find_cycle_sync(pos1: int, n1: int, pos2: int, n2: int) -> tuple[int, int]:
    while pos1 != pos2:
        if pos1 < pos2:
            n_hops = math.ceil((pos2 - pos1) / n1)
            pos1 += n_hops * n1
        else:  # pos1 > pos2
            n_hops = math.ceil((pos1 - pos2) / n2)
            pos2 += n_hops * n2
    return pos1, math.lcm(n1, n2)


def solve2(input_: Input) -> int:
    directions, graph = input_
    n = len(directions)
    # analyze cyclical nature of movements
    cycles = {}
    for name in filter(lambda loc: loc.endswith("A"), graph.keys()):
        states_seen = {}
        z_sequence = []
        cur = name
        for i, i_mod in enumerate(itertools.cycle(range(n))):
            state = (cur, i_mod)
            if state in states_seen:
                break  # about to start looping
            states_seen[state] = i
            z_sequence.append(cur.endswith("Z"))
            cur = _apply_direction(cur, directions[i_mod], graph)
        else:
            raise ValueError("empty list of directions")
        i_start_cycle = states_seen[state]
        intro, cycle = z_sequence[:i_start_cycle], z_sequence[i_start_cycle:]
        cycles[name] = (intro, cycle)
    # check that the input is within the subset that this program can solve
    for intro, cycle in cycles.values():
        if (sum(intro), sum(cycle)) != (0, 1):  # no Z in intros, only 1 Z per cycle
            # TODO: add a semi-smart brute-force as backup
            raise RuntimeError("this code isn't ready to handle more complicated Z-patterns")
    # convert from lists to integers
    intro_lengths = {name: len(intro) for name, (intro, _) in cycles.items()}
    longest_intro = max(intro_lengths.values())
    cycle_lengths = {name: len(cycle) for name, (_, cycle) in cycles.items()}
    z_positions_in_cycles = {name: cycle.index(True) for name, (_, cycle) in cycles.items()}
    # shift the period window of each cycle (roll the cycle) so they all start at the end of the longest intro
    z_positions_in_cycles = {
        name: z_position - ((longest_intro - intro_lengths[name]) % cycle_lengths[name])
        for name, z_position in z_positions_in_cycles.items()
    }
    # "reduce" across `z_positions_in_cycles` using `find_overlap_pos`
    overlap_pos = None
    sync_period = None
    for name, z_pos in z_positions_in_cycles.items():
        if overlap_pos is None:  # first
            overlap_pos = z_pos
            sync_period = cycle_lengths[name]
        else:  # 2nd and others
            overlap_pos, sync_period = find_cycle_sync(
                z_pos, cycle_lengths[name],
                overlap_pos, sync_period,
            )
    if overlap_pos is None:
        raise ValueError("no cycles to sync")
    # fun fact: sync_period == math.lcm(*cycle_lengths.values())
    # adjust pos to account for intros
    first_universal_overlap = longest_intro + overlap_pos
    return first_universal_overlap


def main():
    input_ = read_input()
    answer = solve1(input_)
    pprint(answer)
    answer = solve2(input_)
    pprint(answer)


if __name__ == "__main__":
    main()
