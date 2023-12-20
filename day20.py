from pathlib import Path
from collections import Counter, deque
import re
from abc import ABC
from pprint import pprint

INPUT_FILE_PATH = Path("input.txt")

BUTTON = "BUTTON"
BROADCASTER = "broadcaster"


class Module(ABC):
    def __init__(self, name: str, neighbors: list[str]):
        super().__init__()
        self.name = name
        self.neighbors = neighbors

    def pulse(self, src: str, pulse: bool) -> list[tuple[str, str, bool]]:
        raise NotImplementedError("must be implemented by child class")


class BroadcasterModule(Module):
    def pulse(self, src: str, pulse: bool) -> list[tuple[str, str, bool]]:
        return [
            (self.name, neighbor, pulse)  # just forward it on
            for neighbor in self.neighbors
        ]


class FlipFlopModule(Module):
    def __init__(self, name: str, neighbors: list[str], state: bool = False):
        super().__init__(name, neighbors)
        self.state = state

    def pulse(self, src: str, pulse: bool) -> list[tuple[str, str, bool]]:
        if pulse:  # high pulse does nothing
            return []
        self.state = not self.state
        return [
            (self.name, neighbor, self.state)  # sends new state
            for neighbor in self.neighbors
        ]


class ConjunctionModule(Module):
    def __init__(self, name: str, neighbors: list[str]):
        super().__init__(name, neighbors)
        self.memory: dict[str, bool] = {}

    def register_input(self, input_name: str, start_memory: bool = False):
        self.memory[input_name] = start_memory

    def pulse(self, src: str, pulse: bool) -> list[tuple[str, str, bool]]:
        self.memory[src] = pulse
        if all(self.memory.values()):
            to_send = False
        else:
            to_send = True
        return [
            (self.name, neighbor, to_send)
            for neighbor in self.neighbors
        ]


Input = dict[str, Module]


def read_input() -> Input:
    with open(INPUT_FILE_PATH, "r", encoding="utf-8") as f:
        modules: Input = {}
        for line in f:
            module_type_sym, name, neighbors_str = re.fullmatch(r"([%&]?)(\w+) -> (\w+(?:, \w+)*)", line.strip()).groups()
            neighbors = neighbors_str.split(", ")
            if module_type_sym == "" and name == BROADCASTER:
                module = BroadcasterModule(name, neighbors)
            elif module_type_sym == "%":
                module = FlipFlopModule(name, neighbors)
            elif module_type_sym == "&":
                module = ConjunctionModule(name, neighbors)
            else:
                raise ValueError(f"{line=!r}")
            modules[name] = module
        for module in modules.values():
            for neighbor_name in module.neighbors:
                neighbor = modules.get(neighbor_name)
                if isinstance(neighbor, ConjunctionModule):
                    neighbor.register_input(module.name)
        return modules


def solve(input_: Input) -> int:
    _missing = set()
    n_presses = 1000
    n_pulses = Counter()
    for _ in range(n_presses):
        pulses_q = deque()
        pulses_q.append((BUTTON, BROADCASTER, False))
        while len(pulses_q) > 0:
            src, dest_name, pulse = pulses_q.popleft()
            n_pulses[pulse] += 1
            dest = input_.get(dest_name)
            if dest is None:
                _missing.add(dest_name)
                continue
            new_pulses = dest.pulse(src, pulse)
            pulses_q.extend(new_pulses)
    return n_pulses[False] * n_pulses[True]


def main():
    input_ = read_input()
    answer = solve(input_)
    pprint(answer)


if __name__ == "__main__":
    main()
