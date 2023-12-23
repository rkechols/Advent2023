from pathlib import Path
from pprint import pprint
import numpy as np
from enum import Enum

Input = np.ndarray
Loc = tuple[int, int]

INPUT_FILE_PATH = Path("input.txt")

TREE = "#"
PATH = "."


def read_input() -> Input:
    with open(INPUT_FILE_PATH, "r", encoding="utf-8") as f:
        return np.array([
            [c for c in line.strip()]
            for line in f
        ])


class Direction(Enum):
    RIGHT = (0, 1)
    DOWN = (1, 0)
    LEFT = (0, -1)
    UP = (-1, 0)

    def opposite(self) -> "Direction":
        return self.__class__(tuple(-1 * d for d in self.value))

    def shift(self, loc: Loc) -> Loc:
        new_loc = tuple(d + s for d, s in zip(loc, self.value))
        return new_loc


ICE_TO_DIRECTION = {
    ">": Direction.RIGHT,
    "v": Direction.DOWN,
    "<": Direction.LEFT,
    "^": Direction.UP,
}


def find_junctions(grid: np.ndarray) -> set[Loc]:
    _junctions = set()
    for r, row in enumerate(grid[1:-1], start=1):
        for c, sym in enumerate(row[1:-1], start=1):
            if sym != PATH:
                continue
            loc = (r, c)
            open_neighbors = set()
            for direction in Direction:
                neighbor = direction.shift(loc)
                if grid[neighbor] != TREE:
                    open_neighbors.add(neighbor)
            if len(open_neighbors) != 2:
                _junctions.add(loc)
    return _junctions


class Solver:
    def __init__(self, grid: np.ndarray, *, ignore_ice: bool = False):
        self.ignore_ice = ignore_ice
        if self.ignore_ice:
            grid = grid.copy()
            for r, row in enumerate(grid):
                for c, sym in enumerate(row):
                    if sym in ICE_TO_DIRECTION:
                        grid[r, c] = PATH
        self.grid = grid
        # find start loc
        start_row = 0
        for col, sym in enumerate(self.grid[start_row]):
            if sym != TREE:
                start_col = col
                break
        else:
            raise ValueError("start loc not found")
        self.start_loc = (start_row, start_col)
        # find end loc
        end_row = self.grid.shape[0] - 1
        for col, sym in enumerate(self.grid[end_row]):
            if sym != TREE:
                end_col = col
                break
        else:
            raise ValueError("end loc not found")
        self.end_loc = (end_row, end_col)
        # find junctions
        _junctions = find_junctions(self.grid)
        self.index_to_junction = [self.start_loc] + sorted(_junctions) + [self.end_loc]
        self.junction_to_index = {junction: i for i, junction in enumerate(self.index_to_junction)}
        self.n = len(self.junction_to_index)

    def _trailblaze(self, loc: Loc, seen: set[Loc]) -> tuple[Loc, int] | None:
        steps = 1
        while loc not in self.junction_to_index:
            seen.add(loc)
            sym = self.grid[loc]
            if (ice_direction := ICE_TO_DIRECTION.get(sym)) is not None:
                # currently on ice; forced to move in the direction it points
                next_loc = ice_direction.shift(loc)
            else:  # currently on path; find the one direction available to move
                for direction in Direction:
                    next_loc = direction.shift(loc)
                    if next_loc not in seen:
                        sym = self.grid[next_loc]
                        if sym == TREE:
                            continue
                        if ICE_TO_DIRECTION.get(sym) == direction.opposite():
                            continue  # can't go onto ice that would push us right back
                        # can indeed step here
                        break
                else:  # dead-end but not a junction; probably just hit ice pointing the wrong way
                    # no new junction to record a connection to
                    return None
            # do step in the available direction
            steps += 1
            loc = next_loc
        return loc, steps

    def dfs_longest(self, adjacency: np.ndarray, cur_index: int, cur_dist: int, visited: set[int]) -> int | None:
        if cur_index == self.junction_to_index[self.end_loc]:
            return cur_dist
        longest = None
        for next_index, dist in enumerate(adjacency[cur_index]):
            if dist == 0 or next_index in visited:  # not actually connected, or backtracking
                continue
            result = self.dfs_longest(adjacency, next_index, cur_dist + dist, visited | {next_index})
            if result is None:
                continue
            if longest is None or result > longest:
                longest = result
        return longest

    def solve(self) -> int:
        # make a graph / adjacency matrix between junctions
        adjacency = np.zeros((self.n, self.n), dtype=int)
        # first leg manually
        discovery = self._trailblaze(Direction.DOWN.shift(self.start_loc), {self.start_loc})
        assert discovery is not None
        first_junction, n_steps = discovery
        adjacency[self.junction_to_index[self.start_loc], self.junction_to_index[first_junction]] = n_steps
        searched = {self.start_loc}
        # search through the rest of the map
        to_search = {first_junction}
        while len(to_search) > 0:
            search_start_junction = to_search.pop()
            searched.add(search_start_junction)
            if search_start_junction == self.end_loc:
                continue
            search_start_junction_index = self.junction_to_index[search_start_junction]
            for direction in Direction:
                next_loc = direction.shift(search_start_junction)
                sym = self.grid[next_loc]
                if sym == TREE:
                    continue
                if ICE_TO_DIRECTION.get(sym) == direction.opposite():
                    continue  # can't go onto ice that would push us right back
                # can indeed step here
                discovery = self._trailblaze(next_loc, {search_start_junction})
                if discovery is None:
                    continue
                next_junction, n_steps = discovery
                adjacency[search_start_junction_index, self.junction_to_index[next_junction]] = n_steps
                if next_junction not in searched:
                    to_search.add(next_junction)
        # do a DFS to find the longest path from start to finish
        start_loc_index = self.junction_to_index[self.start_loc]
        return self.dfs_longest(adjacency, start_loc_index, 0, {start_loc_index})


def main():
    input_ = read_input()
    solver = Solver(input_)
    answer = solver.solve()
    pprint(answer)
    solver = Solver(input_, ignore_ice=True)
    answer = solver.solve()
    pprint(answer)


if __name__ == "__main__":
    main()
