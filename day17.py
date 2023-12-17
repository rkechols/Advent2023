from collections import deque
from enum import Enum
from pathlib import Path
from pprint import pprint
from typing import Iterable, Iterator, NamedTuple

import numpy as np

INPUT_FILE_PATH = Path("input.txt")

N_STRAIGHT_LIMIT = 3


def read_input() -> np.ndarray:
    with open(INPUT_FILE_PATH, "r", encoding="utf-8") as f:
        return np.array([
            list(map(int, line.strip()))
            for line in f
        ])


class Direction(Enum):
    UP = (-1, 0)
    LEFT = (0, -1)
    DOWN = (1, 0)
    RIGHT = (0, 1)

    def opposite(self) -> "Direction":
        return type(self)(tuple(-1 * d for d in self.value))

    def next_direcion_options(self, n_straight: int) -> list["Direction"]:
        options = set(type(self))  # all directions
        options.discard(self.opposite())  # no u-turns
        if n_straight >= N_STRAIGHT_LIMIT:
            options.discard(self)  # can't keep going the same direction
        return sorted(options, key=lambda d: d.value, reverse=True)

    def shift(self, loc: tuple[int, int]) -> tuple[int, int]:
        return tuple(d + shift for d, shift in zip(loc, self.value))


class State(NamedTuple):
    loc: tuple[int, int]
    prev_direction: Direction
    n_straight: int
    total_so_far: int

    def dict_key(self) -> tuple:
        return self.loc, self.prev_direction, self.n_straight


class Solver:
    def __init__(self, grid: np.ndarray) -> None:
        if len(grid.shape) != 2:
            raise ValueError("only ready to handle 2D grids")
        self.grid = grid
        self.target = (grid.shape[0] - 1, grid.shape[1] - 1)

    def step(self, state: State, direction: Direction) -> State:
        new_loc = direction.shift(state.loc)
        n_straight = state.n_straight + 1 if direction == state.prev_direction else 1
        total_so_far = state.total_so_far + self.grid[new_loc]
        return State(
            loc=new_loc,
            prev_direction=direction,
            n_straight=n_straight,
            total_so_far=total_so_far,
        )

    def gen_possible_steps(self, state: State) -> Iterable[State]:
        for next_direction in state.prev_direction.next_direcion_options(state.n_straight):
            try:
                new_sol = self.step(state, next_direction)
                if not all(0 <= d < limit for d, limit in zip(new_sol.loc, self.grid.shape)):
                    raise IndexError("out of bounds (sneaky)")
            except IndexError:
                continue  # stay in-bounds
            else:
                yield new_sol

    def solve(self) -> int:
        best = None
        dijk: dict[tuple, int] = {}
        for direction in (Direction.RIGHT, Direction.DOWN):
            loc = direction.shift((0, 0))
            state = State(
                loc=loc,
                prev_direction=direction,
                n_straight=1,
                total_so_far=self.grid[loc],
            )  # technically should check if this has reached the target...
            stack: deque[Iterator[State]] = deque()
            stack.append(self.gen_possible_steps(state))
            while len(stack) > 0:
                possible_next_states = stack[-1]
                try:
                    state = next(possible_next_states)
                except StopIteration:
                    stack.pop()
                else:
                    if state.loc == self.target:  # reached the end
                        if best is None or state.total_so_far < best:
                            best = state.total_so_far
                            continue
                    state_key = state.dict_key()
                    if dijk.get(state_key, float("inf")) <= state.total_so_far:
                        continue
                    dijk[state_key] = state.total_so_far
                    stack.append(self.gen_possible_steps(state))
        return best


def main():
    input_ = read_input()
    solver = Solver(input_)
    import sys
    recursion_limit = sys.getrecursionlimit()
    sys.setrecursionlimit(2000)
    answer = solver.solve()
    sys.setrecursionlimit(recursion_limit)
    pprint(answer)


if __name__ == "__main__":
    main()
