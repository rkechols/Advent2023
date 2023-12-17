import heapq
from enum import Enum
from functools import cache
from pathlib import Path
from pprint import pprint
from typing import Any, Callable, Generic, Iterable, NamedTuple, TypeVar

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

    def next_direcion_options(self, n_straight: int) -> set["Direction"]:
        options = set(type(self))  # all directions
        options.discard(self.opposite())  # no u-turns
        if n_straight >= N_STRAIGHT_LIMIT:
            options.discard(self)  # can't keep going the same direction
        return options

    def shift(self, loc: tuple[int, int]) -> tuple[int, int]:
        return tuple(d + shift for d, shift in zip(loc, self.value))


class State(NamedTuple):
    loc: tuple[int, int]
    prev_direction: Direction
    n_straight: int
    total_so_far: int

    def dict_key(self):
        return self.loc, self.prev_direction, self.n_straight


Key = tuple[int, int]


T = TypeVar("T")


class PriorityQueue(Generic[T]):
    def __init__(self, key: Callable[[T], Key]):
        class _Elem:
            def __init__(self, value: T):
                self.value = value

            def __repr__(self) -> str:
                return f"{self.__class__.__name__}({self.value!r})"

            def __lt__(self, other: Any) -> bool:
                if not isinstance(other, type(self)):
                    return self < other
                return key(self.value) < key(other.value)
        self._Elem = _Elem
        self.data: list[self._Elem] = []

    def __len__(self) -> int:
        return len(self.data)

    def heappush(self, value: T):
        heapq.heappush(self.data, self._Elem(value))

    def heappop(self) -> T:
        elem = heapq.heappop(self.data)
        return elem.value


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

    @cache
    def manhattan(self, loc: tuple[int, int]) -> int:
        return sum(abs(d_dest - d) for d, d_dest in zip(loc, self.target))

    @cache
    def loc_score(self, loc: tuple[int, int]) -> int:
        manhattan = self.manhattan(loc)
        offset_penalty = abs(loc[0] - loc[1])
        score = manhattan + offset_penalty
        return score

    def step_greedy(self, state: State) -> State:
        best_new_sol = None
        best_score = None
        for new_sol in self.gen_possible_steps(state):
            this_score = self.loc_score(new_sol.loc)
            if best_score is None or this_score < best_score:
                best_score = this_score
                best_new_sol = new_sol
        return best_new_sol

    def solve_greedy(self, state: State) -> int:
        seen = set()
        while state.loc != self.target:
            state = self.step_greedy(state)
            # watch for repeated movements
            key = state.dict_key()
            if key in seen:
                raise ValueError("infinite loop in greedy algorithm")
            seen.add(key)
        return state.total_so_far

    @cache
    def lower_bound(self, state: State) -> int:
        manhattan = self.manhattan(state.loc)
        bound = state.total_so_far + manhattan
        return bound

    @cache
    def key(self, state: State) -> Key:
        manhattan = self.manhattan(state.loc)
        return manhattan, state.total_so_far

    def solve(self) -> int:
        best = None
        p_queue = PriorityQueue(key=self.key)
        dijk: dict[tuple, int] = {}
        for direction in (Direction.RIGHT, Direction.DOWN):
            loc = direction.shift((0, 0))
            state = State(
                loc=loc,
                prev_direction=direction,
                n_straight=1,
                total_so_far=self.grid[loc],
            )  # technically should check if this has reached the target...
            dijk[state.dict_key()] = state.total_so_far
            upper_bound = self.solve_greedy(state)
            if best is None or upper_bound < best:
                best = upper_bound
            p_queue.heappush(state)
        while len(p_queue) > 0:
            state = p_queue.heappop()
            if state.total_so_far > dijk.get(state.dict_key(), float("inf")) \
                    or self.lower_bound(state) >= best:
                continue
            for next_state in self.gen_possible_steps(state):
                state_key = next_state.dict_key()
                if next_state.total_so_far >= dijk.get(state_key, float("inf")):
                    continue  # something else has been here already, but this proposed path is no better
                dijk[state_key] = next_state.total_so_far
                lower_bound = self.lower_bound(next_state)
                if next_state.loc == self.target:  # found a way to get to the target
                    # lower_bound is its actual score too
                    best = min(best, lower_bound)
                    continue
                if lower_bound >= best:
                    continue
                p_queue.heappush(next_state)
        return best


def main():
    input_ = read_input()
    solver = Solver(input_)
    answer = solver.solve()
    pprint(answer)


if __name__ == "__main__":
    main()
