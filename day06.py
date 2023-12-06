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
    t_left = 0
    t_right = t_total
    # stop when our window is <4 wide, since we need 4 to have a left, 2 centers, and a right
    while (n_to_test := 1 + t_right - t_left) >= 4:
        t_center = (t_left + t_right) // 2
        t_pre_center = t_center - 1
        # check slope:
        if _evaluate_race(t_total, t_pre_center) < _evaluate_race(t_total, t_center):
            t_left = t_center  # peak is to the right of 'center'
        else:
            t_right = t_pre_center  # peak is to the left of 'center'
    assert 0 < n_to_test < 4
    # brute-force the last few options
    return max(
        range(t_left, t_right + 1),
        key=lambda t_hold: _evaluate_race(t_total, t_hold)
    )


def _find_target_distance(t_left: int, t_right: int, t_total: int, d_target: int, *, reverse: bool) -> int:
    """
    Find the t-value that gets distance equal to `d_target`.
    If `d_target` cannot be produced exactly, return the nearest t-value that
    produces a distance just greater than `d_target`
    Uses a binary search based on the distance yielded from each t-value;
    this requires the assumption that the distances produced by a sequence of t-values are monotonic.
    If increasing t-values yield monotonic *increasing* distances, use `reverse=False`.
    If increasing t-values yield monotonic *decreasing* distances, use `reverse=True`.
    """
    assert 0 <= t_left <= t_right <= t_total
    # check that the target value isn't out of range
    if (
        (not reverse and _evaluate_race(t_total, t_right) < d_target)
        or (reverse and d_target > _evaluate_race(t_total, t_left))
    ):
        raise ValueError("search error: target value is out of range")
    # actually do the search
    while True:
        # calculate d values at boundaries
        d_left = _evaluate_race(t_total, t_left)
        if (
            d_left == d_target  # bullseye
            or (not reverse and d_target < d_left)  # target is already below our search range
        ):
            return t_left
        d_right = _evaluate_race(t_total, t_right)
        if (
            d_right == d_target  # bullseye
            or (reverse and d_right > d_target)  # target is already below our search range
        ):
            return t_right
        # double check monotonic-ness
        if (
            d_left == d_right
            or (not reverse and d_left > d_right)
            or (reverse and d_left < d_right)
        ):
            raise ValueError("search error: values seem to not be monotonic in the specified direction")
        # base case: boundaries are adjacent t-values
        if t_left + 1 == t_right:
            # target must be between the last two options
            if not reverse:
                return t_right  # right side is the one barely over the target
            else:
                return t_left  # left side is the one barely over the target
        # get the center value and
        t_center = (t_left + t_right) // 2
        d_center = _evaluate_race(t_total, t_center)
        if d_center == d_target:  # bullseye
            return t_center
        if (not reverse and d_target < d_center) or (reverse and d_target > d_center):
            t_right = t_center  # target is to the left of 'center'
        elif (not reverse and d_center < d_target) or (reverse and d_center > d_target):
            t_left = t_center  # target is to the right of 'center'
        else:
            raise RuntimeError


def _count_ways_to_win(time_total: int, distance_to_beat: int) -> int:
    t_best_possible = _find_peak(time_total)
    if _evaluate_race(time_total, t_best_possible) <= distance_to_beat:
        return 0
    # binary searches to find the t-values that get the target d
    t_low = _find_target_distance(0, t_best_possible, time_total, distance_to_beat, reverse=False)
    assert _evaluate_race(time_total, t_low) >= distance_to_beat
    t_high = _find_target_distance(t_best_possible, time_total, time_total, distance_to_beat, reverse=True)
    assert _evaluate_race(time_total, t_high) >= distance_to_beat
    # trim boundaries inward
    while _evaluate_race(time_total, t_low) == distance_to_beat and t_low < t_high:
        t_low += 1
    while _evaluate_race(time_total, t_high) == distance_to_beat and t_low < t_high:
        t_high -= 1
    if t_low == t_high:
        # one singular t-value; check if it's a winner
        return int(_evaluate_race(time_total, t_low) > distance_to_beat)
    # how many numbers are in the range?
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
