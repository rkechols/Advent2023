import math
import re
from functools import cache
from pathlib import Path
from pprint import pprint

Input = list[tuple[int, int]]

INPUT_FILE_PATH = Path("input.txt")


def read_input() -> Input:
    with open(INPUT_FILE_PATH, "r", encoding="utf-8") as f:
        times = f.readline()
        distances_to_beat = f.readline()
    times = map(int, re.findall(r"\d+", times))
    distances_to_beat = map(int, re.findall(r"\d+", distances_to_beat))
    return list(zip(times, distances_to_beat))


@cache
def _evaluate_race(time_total: int, time_held: int) -> int:
    assert 0 <= time_held <= time_total
    speed = time_held
    time_moving = time_total - time_held
    distance = time_moving * speed
    return distance


def solve1(input_: Input) -> int:
    n_ways_per_race = []
    for time_total, distance_to_beat in input_:
        for time_held in range(1, time_total):
            result = _evaluate_race(time_total, time_held)
            if result > distance_to_beat:
                min_hold = time_held
                break
        else:  # not possible to beat `distance_to_beat`
            n_ways_per_race.append(0)
            continue
        for time_held in range(time_total - 1, min_hold, -1):
            result = _evaluate_race(time_total, time_held)
            if result > distance_to_beat:
                max_hold = time_held
                break
        else:  # `min_hold` is the only way to beat `distance_to_beat`
            max_hold = min_hold
        n_ways = 1 + max_hold - min_hold
        n_ways_per_race.append(n_ways)
    return math.prod(n_ways_per_race)


# def solve1(input_: Input) -> int:
#     # not so naïve solution
#     return math.prod(
#         _count_ways_to_win(time_total, distance_to_beat)
#         for time_total, distance_to_beat in input_
#     )


def _find_peak(t_total: int) -> int:
    """
    Find the t-value that gets the highest distance.
    Uses a binary search where the slope indicates what direction (lower/higher) to find the maximum
    """
    assert 0 <= t_total
    # boundaries of the binary search, which close in on a solution
    t_min = 0
    t_max = t_total
    # stop when our window is <4 wide, since we need 4 to have a min, 2 middles, and a max
    while (n_to_test := 1 + t_max - t_min) >= 4:
        t_center = (t_min + t_max) // 2
        t_pre_center = t_center - 1
        # check slope:
        if _evaluate_race(t_total, t_pre_center) < _evaluate_race(t_total, t_center):
            t_min = t_center  # peak is to the right of 'center'
        else:
            t_max = t_pre_center  # peak is to the left of 'center'
    assert 0 < n_to_test < 4
    # brute-force the last few options
    if n_to_test == 1:  # not technically necessary; code below could actually still handle this case
        return t_min
    best_t = None
    best_d = None
    for t_hold in range(t_min, t_max + 1):
        this_dist = _evaluate_race(t_total, t_hold)
        if best_t is None or this_dist > best_d:
            best_t = t_hold
            best_d = this_dist
    return best_t


def _binary_search(t_min: int, t_max: int, *, t_total: int, d_target: int, reverse: bool) -> int:
    assert 0 <= t_min <= t_max <= t_total
    d_start = _evaluate_race(t_total, t_min)
    if d_start == d_target:
        return t_min
    d_end = _evaluate_race(t_total, t_max)
    if d_end == d_target:
        return t_max
    if t_min + 1 == t_max:
        if not reverse and (d_start < d_target < d_end):
            return t_max
        elif reverse and (d_end < d_target < d_start):
            return t_min
    if d_start == d_end and d_start != d_target:
        raise ValueError("search edges are equal to each other, but not equal to the target")
    assert (d_start < d_end) == (not reverse)
    if (d_start < d_end and not (d_start <= d_target <= d_end)) or \
            (d_end < d_start and not (d_end <= d_target <= d_start)):
        raise ValueError("impossible search")
    t_center = (t_min + t_max) // 2
    d_center = _evaluate_race(t_total, t_center)
    if d_center == d_target:
        return t_center
    if (d_target < d_center and not reverse) or (d_center < d_target and reverse):
        return _binary_search(t_min, t_center, t_total=t_total, d_target=d_target, reverse=reverse)
    elif (d_target < d_center and reverse) or (d_center < d_target and not reverse):
        return _binary_search(t_center, t_max, t_total=t_total, d_target=d_target, reverse=reverse)
    else:
        raise RuntimeError("bad code 😅")


def _count_ways_to_win(time_total: int, distance_to_beat: int) -> int:
    t_best_possible = _find_peak(time_total)
    if _evaluate_race(time_total, t_best_possible) <= distance_to_beat:
        return 0
    # binary searches to find the t-values that get the target d
    t_low = _binary_search(0, t_best_possible, t_total=time_total, d_target=distance_to_beat, reverse=False)
    assert _evaluate_race(time_total, t_low) >= distance_to_beat
    t_high = _binary_search(t_best_possible, time_total, t_total=time_total, d_target=distance_to_beat, reverse=True)
    assert _evaluate_race(time_total, t_high) >= distance_to_beat
    # trim boundaries inward
    while _evaluate_race(time_total, t_low) == distance_to_beat and t_low < t_high:
        t_low += 1
    while _evaluate_race(time_total, t_high) == distance_to_beat and t_low < t_high:
        t_high -= 1
    if t_low == t_high:
        return int(_evaluate_race(time_total, t_low) > distance_to_beat)
    return 1 + t_high - t_low


def solve2(input_: Input) -> int:
    time_total = int("".join(map(str, (t for t, _ in input_))))
    distance_to_beat = int("".join(map(str, (d for _, d in input_))))
    return _count_ways_to_win(time_total, distance_to_beat)


def main():
    input_ = read_input()
    answer = solve1(input_)
    pprint(answer)
    answer = solve2(input_)
    pprint(answer)


if __name__ == "__main__":
    main()
