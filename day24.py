from tqdm import tqdm
from pathlib import Path
from pprint import pprint
import numpy as np
import multiprocessing as mp

Triple = tuple[int, int, int]
Input = list[tuple[Triple, Triple]]

INPUT_FILE_PATH = Path("input.txt")

VAL_MIN = 200000000000000
VAL_MAX = 400000000000000
_dtype = np.float64


def read_input() -> Input:
    with open(INPUT_FILE_PATH, "r", encoding="utf-8") as f:
        return [
            tuple(
                tuple(map(int, triple_raw.strip().split(", ")))
                for triple_raw in line.split("@")
            )
            for line in f
        ]


n_parallel = 0
n_past = 0
n_intersect = 0
n_oob = 0


def get_intersection(hail_i: tuple[np.ndarray, np.ndarray], hail_j: tuple[np.ndarray, np.ndarray]) -> tuple[float, np.ndarray] | None:
    p0_i, v_i = hail_i
    p0_j, v_j = hail_j
    if np.isclose(1, np.abs(np.dot(v_i, v_j)) / (np.linalg.norm(v_i) * (np.linalg.norm(v_j)))):
        global n_parallel
        n_parallel += 1
        return None  # parallel
    # vx_i * t_i + x0_i = vx_j * t_j + x0_j
    # vy_i * t_i + y0_i = vy_j * t_j + y0_j
    # (vx_i * t_i) + (-1 * vx_j * t_j) = (x0_j - x0_i)
    # (vy_i * t_i) + (-1 * vy_j * t_j) = (y0_j - y0_i)
    a = np.stack([v_i, -1 * v_j], axis=1)
    b = p0_j - p0_i
    t_solution = np.linalg.solve(a, b)
    if np.any(t_solution < 0):
        global n_past
        n_past += 1
        return None  # intersection in the past
    # if not np.isclose(*t_solution):
    #     return None  # lines intersect, but they aren't at the intersection at the same time
    xy_i = p0_i + v_i * t_solution[0]
    xy_j = p0_j + v_j * t_solution[1]
    if not np.allclose(xy_i, xy_j):
        raise ValueError  # numerical error
    global n_intersect
    n_intersect += 1
    return t_solution[0], xy_i


def solve(input_: Input) -> int:
    input_np = [
        tuple(
            np.array(triple, dtype=_dtype)[:2] for triple in hail
        )
        for hail in input_
    ]
    count = 0
    # with mp.Pool(8) as pool:
    for i, hail_i in enumerate(tqdm(input_np)):
        j_start = i + 1
        for j, hail_j in enumerate(input_np[j_start:], start=j_start):
            intersection = get_intersection(hail_i, hail_j)
            if intersection is not None:
                t, xy = intersection
                if t > 0 and all(VAL_MIN <= val <= VAL_MAX for val in xy):
                    count += 1
                else:
                    global n_oob
                    n_oob += 1
    return count


def main():
    input_ = read_input()
    answer = solve(input_)
    pprint(answer)
    print(f"{n_parallel=}")
    print(f"{n_past=}")
    print(f"{n_intersect=}")
    print(f"{n_oob=}")


if __name__ == "__main__":
    main()
