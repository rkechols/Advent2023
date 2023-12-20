import itertools
from pprint import pprint
import random
import re
from abc import ABC
from collections import Counter, deque
from pathlib import Path

import torch

_device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

INPUT_FILE_PATH = Path("input.txt")

BUTTON = "BUTTON"
BROADCASTER = "broadcaster"
MAGIC_MACHINE = "rx"


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


class ModuleSystem:
    def __init__(self, is_flipflop: torch.Tensor, is_conjunction: torch.Tensor, adjacency: torch.Tensor,state: torch.Tensor):
        self.is_flipflop = is_flipflop
        self.is_conjunction = is_conjunction
        self.adjacency = adjacency
        self.state = state
        self.n = is_flipflop.shape[0]

    @classmethod
    def from_input(cls, input_: Input) -> "ModuleSystem":
        # collect ALL names, and map them to indices
        all_names = set()
        for name, module in input_.items():
            all_names.add(name)
            all_names.update(module.neighbors)
        all_names -= {BROADCASTER, MAGIC_MACHINE}
        index_to_name = [BROADCASTER] + sorted(all_names) + [MAGIC_MACHINE]
        name_to_index = {name: i for i, name in enumerate(index_to_name)}
        n = len(name_to_index)
        # module type masks / vectors
        is_flipflop = torch.zeros(n, dtype=torch.int8, device=_device)
        is_conjunction = torch.zeros(n, dtype=torch.int8, device=_device)
        for name, module in input_.items():
            i = name_to_index[name]
            if isinstance(module, FlipFlopModule):
                is_flipflop[i] = 1
            elif isinstance(module, ConjunctionModule):
                is_conjunction[i] = 1
        # build adjacency matrix
        adjacency = torch.zeros(
            (n, n),
            dtype=torch.int8,
            device=_device,
        )
        for name, module in input_.items():
            i = name_to_index[name]
            for neighbor_name in module.neighbors:
                j = name_to_index[neighbor_name]
                adjacency[i, j] = 1  # mark j as a neighbor when coming from i
        # build state matrix
        state = torch.ones(  # ConjunctionModule memory for non-inputs is "high" so checking if all are high can work without a mask
            (n, n),
            dtype=torch.int8,
            device=_device,
        )
        for name, module in input_.items():
            i = name_to_index[name]
            if isinstance(module, FlipFlopModule):
                state[i] = -1  # write the whole row as "off"
            elif isinstance(module, ConjunctionModule):
                for neighbor_name in module.memory.keys():
                    j = name_to_index[neighbor_name]
                    adjacency[i, j] = -1  # start with memory of a low pulse
        # construct
        return cls(
            is_flipflop=is_flipflop,
            is_conjunction=is_conjunction,
            adjacency=adjacency,
            state=state,
        )

    def solve2(self) -> int:
        broadcaster_index = 0
        magical_machine_index = -1
        # start simulating
        n_low = 0
        n_high = 0
        broadcaster_neighbors = self.adjacency[broadcaster_index]
        broadcaster_pulse_batch = (
            broadcaster_neighbors * -1,  # all low pulses
            torch.where(broadcaster_neighbors == 1, broadcaster_index, -1),  # source indices (-1 means N/A)
        )
        for n_button_presses in itertools.count(1):
            n_low += 1  # pulse from the button to the broadcaster
            pulse_batches = deque()
            pulse_batches.append(broadcaster_pulse_batch)
            while len(pulse_batches) > 0:
                pulses_in, pulse_sources = pulse_batches.popleft()
                # check for termination
                if pulses_in[magical_machine_index] == -1:
                    return n_button_presses
                # count each kind of pulse
                n_low += torch.sum(pulses_in == -1)
                n_high += torch.sum(pulses_in == 1)
                # handle (low) pulses coming into flip-flop modules
                indices_flipflops = torch.nonzero((pulses_in * self.is_flipflop) == -1).squeeze_(-1)
                self.state[indices_flipflops] *= -1
                vecs_new_state = self.state[indices_flipflops]
                vecs_dests = self.adjacency[indices_flipflops]
                pulses_new = vecs_new_state * vecs_dests
                pulse_sources_new = torch.where(pulses_new == 0, -1, indices_flipflops.unsqueeze(-1))
                pulse_batches.extend(
                    (p, p_sources)
                    for p, p_sources in zip(pulses_new, pulse_sources_new)
                )
                # handle pulses coming into conjunction modules
                indices_conjunctions = torch.nonzero((pulses_in * self.is_conjunction) != 0).squeeze(-1)
                source_indices = pulse_sources[indices_conjunctions]
                self.state[indices_conjunctions, source_indices] = pulses_in[indices_conjunctions]
                to_send = torch.all(self.state[indices_conjunctions] == 1, dim=1)
                to_send = (to_send.to(dtype=torch.int8) * 2) - 1
                vecs_dests = self.adjacency[indices_conjunctions]
                pulses_new = to_send.unsqueeze(-1) * vecs_dests
                pulse_sources_new = torch.where(pulses_new == 0, -1, indices_conjunctions.unsqueeze(-1))
                pulse_batches.extend(
                    (p, p_sources)
                    for p, p_sources in zip(pulses_new, pulse_sources_new)
                )


def solve(input_: Input):
    part1_solved = False
    part2_solved = False
    n_presses_target = 1000
    n_pulses = Counter()
    for press_num in itertools.count(1):
        pulses_q = deque()
        pulses_q.append((BUTTON, BROADCASTER, False))
        while len(pulses_q) > 0:
            src, dest_name, pulse = pulses_q.popleft()
            if dest_name == MAGIC_MACHINE and not pulse:
                print(f"part 2: {press_num}")
                part2_solved = True
                if part1_solved and part2_solved:
                    return
            n_pulses[pulse] += 1
            dest = input_.get(dest_name)
            if dest is None:
                continue
            new_pulses = dest.pulse(src, pulse)
            random.shuffle(new_pulses)
            pulses_q.extend(new_pulses)
        if press_num == n_presses_target:
            prod = n_pulses[False] * n_pulses[True]
            print(f"part 1: {prod}")
            part1_solved = True
            if part1_solved and part2_solved:
                return


def main():
    input_ = read_input()
    system = ModuleSystem.from_input(input_)
    answer = system.solve2()
    pprint(answer)


if __name__ == "__main__":
    with torch.no_grad():
        main()
