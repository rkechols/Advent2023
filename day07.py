import itertools
from collections import Counter, defaultdict
from enum import Enum
from pathlib import Path
from pprint import pprint

Input = list[tuple[str, int]]

INPUT_FILE_PATH = Path("input.txt")


class HandType(Enum):
    FIVE = 7
    FOUR = 6
    FULL_HOUSE = 5
    THREE = 4
    TWO_PAIR = 3
    ONE_PAIR = 2
    HIGH_CARD = 1

    @classmethod
    def from_hand(cls, hand: str) -> "HandType":
        assert len(hand) == 5
        counter = Counter(hand)
        counts = sorted(counter.values())
        match counts:
            case [5]:  # yahtzee!
                return HandType.FIVE
            case [1, 4]:
                return HandType.FOUR
            case [2, 3]:
                return HandType.FULL_HOUSE
            case [1, 1, 3]:
                return HandType.THREE
            case [1, 2, 2]:
                return HandType.TWO_PAIR
            case [1, 1, 1, 2]:
                return HandType.ONE_PAIR
            case [1, 1, 1, 1, 1]:
                return HandType.HIGH_CARD
            case _:
                raise ValueError(counter)


HAND_TYPE_ORDER = sorted(HandType, key=lambda ht: ht.value)


def card_value(card: str) -> int:
    assert len(card) == 1
    try:
        return int(card)
    except ValueError:
        pass
    match card:
        case "T":
            return 10
        case "J":
            return 11
        case "Q":
            return 12
        case "K":
            return 13
        case "A":
            return 14
        case _:
            raise ValueError(card)


def read_input() -> Input:
    with open(INPUT_FILE_PATH, "r", encoding="utf-8") as f:
        return [
            ((line_split := line_.split())[0], int(line_split[1]))
            for line in f.readlines()
            if (line_ := line.strip()) != ""
        ]


def hand_sorting_key(hand: str) -> list[int]:
    return [
        card_value(card)
        for card in hand
    ]


def solve(input_: Input) -> int:
    hands_with_keys = [
        (hand_sorting_key(hand), hand, bet)
        for hand, bet in input_
    ]
    hands_grouped_by_type = defaultdict(list)
    for hand_tuple in hands_with_keys:
        hand_type = HandType.from_hand(hand_tuple[1])
        hands_grouped_by_type[hand_type].append(hand_tuple)
    for hand_list in hands_grouped_by_type.values():
        hand_list.sort()  # in-place
    overall_sorting = list(itertools.chain(  # concatenate lists
        *(hands_grouped_by_type[hand_type] for hand_type in HAND_TYPE_ORDER)
    ))
    total_winnings = sum(
        rank * hand_tuple[-1]
        for rank, hand_tuple in enumerate(overall_sorting, start=1)
    )
    return total_winnings


def main():
    input_ = read_input()
    answer = solve(input_)
    pprint(answer)


if __name__ == "__main__":
    main()
