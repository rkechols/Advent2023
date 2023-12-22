import copy
import functools
import heapq
from collections import defaultdict
import itertools
from pathlib import Path
from pprint import pprint
from typing import Any, Callable, Generic, Iterable, Sequence, TypeVar

INPUT_FILE_PATH = Path("input.txt")

T = TypeVar("T")

Point = tuple[int, int, int]
Block = tuple[Point, Point]
Input = list[Block]


def min_on_dim(it: Iterable[Sequence[T]], *, dim: int) -> T:
    return min(seq[dim] for seq in it)


def max_on_dim(it: Iterable[Sequence[T]], *, dim: int) -> T:
    return max(seq[dim] for seq in it)


def read_input() -> Input:
    with open(INPUT_FILE_PATH, "r", encoding="utf-8") as f:
        return [
            tuple(
                tuple(map(int, point_raw.split(",")))
                for point_raw in line.strip().split("~")
            )
            for line in f
        ]


def gen_xy_points(block: Block) -> Iterable[tuple[int, int]]:
    for xy in itertools.product(*(
        range(min_on_dim(block, dim=dim), 1 + max_on_dim(block, dim=dim))
        for dim in range(2)
    )):
        yield xy


def gen_xyz_points(block: Block) -> Iterable[Point]:
    for xyz in itertools.product(*(
        range(min_on_dim(block, dim=dim), 1 + max_on_dim(block, dim=dim))
        for dim in range(3)
    )):
        yield xyz


def solve(blocks: Input) -> int:
    # sort block by z-value, ascending
    blocks = sorted(blocks, key=functools.partial(min_on_dim, dim=-1))
    # simulate the blocks falling/landing
    xy_highest: dict[tuple[int, int], int] = defaultdict(int)
    blocks_settled = []
    for block in blocks:
        z_min = min_on_dim(block, dim=-1)
        # figure out how far to fall before landing on something
        smallest_z_gap = None
        for x, y in gen_xy_points(block):
            fall_size = z_min - xy_highest[x, y] - 1
            assert fall_size >= 0
            if smallest_z_gap is None or fall_size < smallest_z_gap:
                smallest_z_gap = fall_size
        assert smallest_z_gap is not None
        assert smallest_z_gap >= 0
        # new position of the block after falling
        if smallest_z_gap == 0:
            block_new = block
        else:
            block_new = tuple(
                (x, y, z - smallest_z_gap)
                for x, y, z in block
            )
        blocks_settled.append(block_new)
        z_max = max_on_dim(block_new, dim=-1)
        for xy in gen_xy_points(block_new):
            xy_highest[xy] = z_max
    blocks = blocks_settled
    # register occupied space
    point_to_block_num: dict[Point, int] = {}
    for block_num, block in enumerate(blocks):
        for point in gen_xyz_points(block):
            point_to_block_num[point] = block_num
    # part 1: figure out which settled blocks would cause something to fall if removed
    count = 0
    for block_num, block in enumerate(blocks):
        z_max = max_on_dim(block, dim=-1)
        block_nums_above = set()
        for x, y in gen_xy_points(block):
            if (block_num_above := point_to_block_num.get((x, y, z_max + 1))) is not None:
                block_nums_above.add(block_num_above)
        if len(block_nums_above) == 0:
            count += 1
            continue
        for block_num_above in block_nums_above:
            block_above = blocks[block_num_above]
            z_min = min_on_dim(block_above, dim=-1)
            if all(
                point_to_block_num.get((x_up, y_up, z_min - 1), block_num) in (block_num, block_num_above)
                for x_up, y_up in gen_xy_points(block_above)
            ):  # all spots below the upper block would be empty upon removal of the block in question
                break
        else:
            count += 1
    yield count
    # part 2: figure out how many blocks we can get to fall by disintegrating just 1
    n_to_fall = sum(
        solve2(block_num_del, block_del, blocks, point_to_block_num)
        for block_num_del, block_del in enumerate(blocks)
    )
    yield n_to_fall


Key = int


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


def solve2(
        block_num_del: int,
        block_del: Block,
        blocks: list[Block],
        point_to_block_num: dict[Point, int],
) -> int:
    # copy things we'll edit in-place
    blocks = copy.deepcopy(blocks)
    point_to_block_num = copy.deepcopy(point_to_block_num)
    # make a priority queue sorted by z value
    p_queue: PriorityQueue[int] = PriorityQueue(lambda block_num: min(p[-1] for p in blocks[block_num]))
    queue_blacklist = {block_num_del}  # to help avoid uneccessary computation
    for x, y, z in gen_xyz_points(block_del):
        del point_to_block_num[x, y, z]
        if (block_num_above := point_to_block_num.get((x, y, z + 1), block_num_del)) != block_num_del:
            if block_num_above not in queue_blacklist:
                p_queue.heappush(block_num_above)
                queue_blacklist.add(block_num_above)
    count = 0
    while len(p_queue) > 0:
        block_num = p_queue.heappop()
        block = blocks[block_num]
        # list any blocks above the current one
        z_max = max(p[-1] for p in block)
        block_nums_above = set()
        for x, y in gen_xy_points(block):
            try:
                block_num_above = point_to_block_num[x, y, z_max + 1]
            except KeyError:
                pass
            else:
                block_nums_above.add(block_num_above)
        # will this one fall?
        z_min = min(p[-1] for p in block)
        smallest_z_gap = None
        for x, y in gen_xy_points(block):
            for z_down in range(z_min - 1, -1, -1):
                if (x, y, z_down) in point_to_block_num:
                    fall_size = z_min - z_down - 1
                    break
            else:
                fall_size = z_min - 1
            assert fall_size >= 0
            if smallest_z_gap is None or fall_size < smallest_z_gap:
                smallest_z_gap = fall_size
        assert smallest_z_gap is not None
        assert smallest_z_gap >= 0
        if smallest_z_gap == 0:  # will not fall; add ones sitting on it to blacklist and move on
            queue_blacklist.update(block_nums_above)
        else:  # will fall
            count += 1
            # execute the fall
            block_new = tuple(
                (x, y, z - smallest_z_gap)
                for x, y, z in block
            )
            blocks[block_num] = block_new
            for point in gen_xyz_points(block):
                del point_to_block_num[point]
            for point in gen_xyz_points(block_new):
                point_to_block_num[point] = block_num
            # add ones above it to queue
            for block_num_above in block_nums_above:
                if block_num_above not in queue_blacklist:
                    p_queue.heappush(block_num_above)
                    queue_blacklist.add(block_num_above)
    return count


# TODO: where possible, replace gen_xyz_points with gen_xy_points


def main():
    input_ = read_input()
    for answer in solve(input_):
        pprint(answer)


if __name__ == "__main__":
    main()
