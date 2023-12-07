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
    def from_hand1(cls, hand: str) -> "HandType":
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

    @classmethod
    def from_hand2(cls, hand: str) -> "HandType":
        assert len(hand) == 5
        if "J" not in hand:  # no jokers; sort it out the normal way
            return cls.from_hand1(hand)
        counter = Counter(hand)
        n_jokers = counter.pop("J")
        if len(counter) <= 1:  # all actual cards are the same; match the jokers to them
            return HandType.FIVE  # yahtzee!
        if n_jokers == 3:  # 2 actual cards; they don't match
            return HandType.FOUR
        counts = sorted(counter.values())
        if n_jokers == 2:  # 3 actual cards; not all the same
            match counts:
                case [1, 1, 1]:  # both jokers go with any (better than splitting to get 2-pair)
                    return HandType.THREE
                case [1, 2]:  # jokers go with the pair
                    return HandType.FOUR
                case _:
                    raise ValueError(counts)
        # 4 actual cards; not all the same
        assert n_jokers == 1
        match counts:
            case [1, 3]:  # joker goes with the triple
                return HandType.FOUR
            case [2, 2]:
                return HandType.FULL_HOUSE
            case [1, 1, 2]:  # joker goes with pair, since 3-of-a-kind is better than 2-pair
                return HandType.THREE
            case [1, 1, 1, 1]:  # no comment
                return HandType.ONE_PAIR
            case _:
                raise ValueError(counts)


HAND_TYPE_ORDER = sorted(HandType, key=lambda ht: ht.value)


def card_value(card: str, *, j_is_joker: bool) -> int:
    assert len(card) == 1
    try:
        return int(card)
    except ValueError:
        pass
    match card:
        case "T":
            return 10
        case "J":
            return 1 if j_is_joker else 11
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


def hand_sorting_key1(hand: str) -> list[int]:
    return [
        card_value(card, j_is_joker=False)
        for card in hand
    ]


def solve1(input_: Input) -> int:
    hands_with_keys = [
        (hand_sorting_key1(hand), hand, bet)
        for hand, bet in input_
    ]
    hands_grouped_by_type = defaultdict(list)
    for hand_tuple in hands_with_keys:
        hand_type = HandType.from_hand1(hand_tuple[1])
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


def hand_sorting_key2(hand: str) -> list[int]:
    return [
        card_value(card, j_is_joker=True)
        for card in hand
    ]


def solve2(input_: Input) -> int:
    hands_with_keys = [
        (hand_sorting_key2(hand), hand, bet)
        for hand, bet in input_
    ]
    hands_grouped_by_type = defaultdict(list)
    for hand_tuple in hands_with_keys:
        hand_type = HandType.from_hand2(hand_tuple[1])
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
    answer = solve1(input_)
    pprint(answer)
    answer = solve2(input_)
    pprint(answer)


if __name__ == "__main__":
    main()
