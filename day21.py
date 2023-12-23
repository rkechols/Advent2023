from enum import Enum
from pathlib import Path
from pprint import pprint

import numpy as np

Loc = tuple[int, int]
Input = tuple[np.ndarray, Loc]  # 2D, bools

INPUT_FILE_PATH = Path("input.txt")

START = "S"
ROCK = "#"


class Direction(Enum):
    RIGHT = (1, 0)
    DOWN = (0, -1)
    LEFT = (-1, 0)
    UP = (0, 1)

    def shift(self, loc: Loc) -> Loc:
        new_loc = tuple(d + s for d, s in zip(loc, self.value))
        return new_loc


def read_input() -> Input:
    grid = []
    start_loc = None
    with open(INPUT_FILE_PATH, "r", encoding="utf-8") as f:
        for r, line_ in enumerate(f):
            line = line_.strip()
            for c, s in enumerate(line):
                if s == START:
                    start_loc = (r, c)
            row = [s != ROCK for s in line]
            grid.append(row)
    grid = np.array(grid)
    return grid, start_loc


def visualize(input_: Input):
    grid, start_loc = input_
    canvas = grid.astype(np.uint8) * 255
    canvas = np.stack([canvas] * 3, axis=-1)
    canvas[start_loc] = (255, 0, 0)
    from PIL import Image
    image = Image.fromarray(canvas)
    image.save("inputs/day21.png")
    image.show()


def solve1(input_: Input, n_steps: int) -> int:
    grid, start_loc = input_
    # pad with all rocks to simplify out-of-bounds checking
    grid = np.pad(grid, 1, constant_values=False)
    start_loc = tuple(d + 1 for d in start_loc)
    # BFS-like search
    parity = n_steps % 2
    seen_locs: set[Loc] = set()  # don't repeat / backtrack into known territory
    possible_locs: set[Loc] = set()  # answer
    search_locs = {start_loc}  # "queue" of current possible positions
    for step_num in range(n_steps + 1):
        if step_num % 2 == parity:
            possible_locs.update(search_locs)
        seen_locs.update(search_locs)
        search_locs_next = set()  # next layer of possible positions
        for search_loc in search_locs:
            for direction in Direction:
                neighbor_loc = direction.shift(search_loc)
                if grid[neighbor_loc] and neighbor_loc not in seen_locs:
                    search_locs_next.add(neighbor_loc)
        search_locs = search_locs_next
    return len(possible_locs)


BoardLoc = tuple[int, int]
InfiniteLoc = tuple[Loc, BoardLoc]


def wrap(loc: Loc, grid_shape: tuple[int, int]) -> Loc:
    return tuple(d % n for d, n in zip(loc, grid_shape))


def solve2(input_: Input, n_steps: int) -> int:
    grid, start_loc = input_
    seen = set()
    to_search = {start_loc}
    while len(to_search) > 0:
        loc = to_search.pop()
        seen.add(loc)
        for direction in Direction:
            new_loc = wrap(direction.shift(loc), grid.shape)
            if grid[new_loc] and new_loc not in seen:
                to_search.add(new_loc)
    # adjacency matrix
    index_to_loc = list(seen)
    n = len(index_to_loc)
    adjacency = np.empty((n, n), dtype=bool)
    for i, loc in enumerate(index_to_loc):
        neighbors = {wrap(direction.shift(loc), grid.shape) for direction in Direction}
        for j, other_loc in enumerate(index_to_loc):
            if other_loc in neighbors:
                adjacency[i, j] = True
            else:
                adjacency[i, j] = False
    adjacency = adjacency.T  # for standard matrix multiplication
    # adjacency matrix for exactly n_steps down the line
    adjacency_n_steps = np.linalg.matrix_power(adjacency, n_steps)
    # see where we can get based on our start position
    start_state = np.zeros(n, dtype=bool)
    start_loc_index = index_to_loc.index(start_loc)
    start_state[start_loc_index] = True
    final_state = np.matmul(adjacency_n_steps, start_state)
    answer = final_state.sum()
    return answer


def main():
    input_ = read_input()
    visualize(input_)
    answer = solve1(input_, n_steps=64)
    pprint(answer)
    answer = solve2(input_, n_steps=1000)
    # answer = solve2(input_, n_steps=26501365)
    pprint(answer)


if __name__ == "__main__":
    main()
