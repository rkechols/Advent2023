from pathlib import Path
import z3
from pprint import pprint

import numpy as np
from tqdm import tqdm

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


def get_intersection(hail_i: tuple[np.ndarray, np.ndarray], hail_j: tuple[np.ndarray, np.ndarray]) -> tuple[float, np.ndarray] | None:
    p0_i, v_i = hail_i
    p0_j, v_j = hail_j
    if np.isclose(1, np.abs(np.dot(v_i, v_j)) / (np.linalg.norm(v_i) * (np.linalg.norm(v_j)))):
        return None  # parallel
    # vx_i * t_i + x0_i = vx_j * t_j + x0_j
    # vy_i * t_i + y0_i = vy_j * t_j + y0_j
    # (vx_i * t_i) + (-1 * vx_j * t_j) = (x0_j - x0_i)
    # (vy_i * t_i) + (-1 * vy_j * t_j) = (y0_j - y0_i)
    a = np.stack([v_i, -1 * v_j], axis=1)
    b = p0_j - p0_i
    t_solution = np.linalg.solve(a, b)
    if np.any(t_solution < 0):
        return None  # intersection in the past
    # if not np.isclose(*t_solution):
    #     return None  # lines intersect, but they aren't at the intersection at the same time
    xy_i = p0_i + v_i * t_solution[0]
    xy_j = p0_j + v_j * t_solution[1]
    if not np.allclose(xy_i, xy_j):
        raise ValueError  # numerical error
    return t_solution[0], xy_i


def solve1(input_: Input) -> int:
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
    return count


def solve2(input_: Input) -> int:
    # input_np = [
    #     tuple(
    #         np.array(triple, dtype=_dtype) for triple in hail
    #     )
    #     for hail in input_[:3]
    # ]
    """
    p0 + v * t = p

    [*] 211614908752320 + 15 * t_i = x0 + vx * t_i
    [*] 355884497165907 + -119 * t_i = y0 + vy * t_i
    [*] 259696313651729 + 26 * t_i = z0 + vz * t_i
    [ ] 403760160726375 + -18 * t_j = x0 + vx * t_j
    [ ] 378047702508912 + -130 * t_j = y0 + vy * t_j
    [ ] 174017730109516 + 147 * t_j = z0 + vz * t_j
    [ ] 144186255945915 + -7 * t_k = x0 + vx * t_k
    [ ] 328686782113692 + 147 * t_k = y0 + vy * t_k
    [ ] 276690520845056 + -255 * t_k = z0 + vz * t_k

    211614908752320 + 15 * t_i = x0 + vx * t_i
    211614908752320 + (15 - vx) * t_i = x0
    (15 - vx) * t_i = x0 - 211614908752320
    t_i = (x0 - 211614908752320) / (15 - vx)
    t_i = (y0 - 355884497165907) / (-119 - vy)
    t_i = (z0 - 259696313651729) / (26 - vz)

    [ ] (x0 - 211614908752320) / (15 - vx) = (y0 - 355884497165907) / (-119 - vy)
    [ ] (x0 - 211614908752320) / (15 - vx) = (z0 - 259696313651729) / (26 - vz)
    [ ] (x0 - 403760160726375) / (-18 - vx) = (y0 - 378047702508912) / (-130 - vy)
    [ ] (x0 - 403760160726375) / (-18 - vx) = (z0 - 174017730109516) / (147 - vz)
    [ ] (x0 - 144186255945915) / (-7 - vx) = (y0 - 328686782113692) / (147 - vy)
    [ ] (x0 - 144186255945915) / (-7 - vx) = (z0 - 276690520845056) / (-255 - vz)
    """

    s = z3.Solver()
    x0 = z3.Int("x0")
    y0 = z3.Int("y0")
    z0 = z3.Int("z0")
    vx = z3.Int("vx")
    vy = z3.Int("vy")
    vz = z3.Int("vz")
    s.add((x0 - 211614908752320) / (15 - vx) == (y0 - 355884497165907) / (-119 - vy))
    s.add((x0 - 211614908752320) / (15 - vx) == (z0 - 259696313651729) / (26 - vz))
    s.add((x0 - 403760160726375) / (-18 - vx) == (y0 - 378047702508912) / (-130 - vy))
    s.add((x0 - 403760160726375) / (-18 - vx) == (z0 - 174017730109516) / (147 - vz))
    s.add((x0 - 144186255945915) / (-7 - vx) == (y0 - 328686782113692) / (147 - vy))
    s.add((x0 - 144186255945915) / (-7 - vx) == (z0 - 276690520845056) / (-255 - vz))
    s.check()
    m = s.model()
    p0 = np.array([m[var_].as_long() for var_ in (x0, y0, z0)])
    v = np.array([m[var_].as_long() for var_ in (vx, vy, vz)])
    print(f"{p0=}")
    print(f"{v=}")
    return p0.sum()  # 2834583825026667 is too high


def main():
    input_ = read_input()
    # answer = solve1(input_)
    # pprint(answer)
    answer = solve2(input_)
    pprint(answer)


if __name__ == "__main__":
    main()
