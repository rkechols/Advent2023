import itertools
from collections import Counter, defaultdict
from enum import Enum
from pathlib import Path
from pprint import pprint

Input = list[tuple[str, int]]

INPUT_FILE_PATH = Path("input.txt")


class HandType(Enum):
    # numeric values represent the relative values of the hand types
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
                return cls.FIVE
            case [1, 4]:
                return cls.FOUR
            case [2, 3]:
                return cls.FULL_HOUSE
            case [1, 1, 3]:
                return cls.THREE
            case [1, 2, 2]:
                return cls.TWO_PAIR
            case [1, 1, 1, 2]:
                return cls.ONE_PAIR
            case [1, 1, 1, 1, 1]:  # good luck with that
                return cls.HIGH_CARD
            case _:
                raise ValueError(f"{counter=}")

    @classmethod
    def from_hand_with_jokers(cls, hand: str) -> "HandType":
        assert len(hand) == 5
        if "J" not in hand:  # no jokers; sort it out the normal way
            return cls.from_hand(hand)
        counter = Counter(hand)
        n_jokers = counter.pop("J")
        if len(counter) <= 1:  # all actual cards are the same; match the jokers to them
            # note that this case catches when there are 5 or 4 jokers
            return cls.FIVE  # yahtzee!
        if n_jokers == 3:  # 2 actual cards (they don't match)
            return cls.FOUR
        counts = sorted(counter.values())
        if n_jokers == 2:  # 3 actual cards (they don't all match)
            match counts:
                case [1, 1, 1]:
                    return cls.THREE
                case [1, 2]:
                    return cls.FOUR
                case _:
                    raise ValueError(f"{counter=}")
        assert n_jokers == 1  # 4 actual cards (they don't all match)
        match counts:
            case [1, 3]:
                return cls.FOUR
            case [2, 2]:
                return cls.FULL_HOUSE
            case [1, 1, 2]:
                return cls.THREE
            case [1, 1, 1, 1]:  # oof
                return cls.ONE_PAIR
            case _:
                raise ValueError(f"{counter=}")


# hand types in order from worst to best
HAND_TYPE_ORDER = sorted(HandType, key=lambda ht: ht.value)

CARD_ORDER = "23456789TJQKA"


def card_value(card: str, *, j_is_joker: bool) -> int:
    assert len(card) == 1, "card should be a single char"
    if j_is_joker and card == "J":
        return -float("inf")
    return 1 + CARD_ORDER.index(card)


def hand_sorting_key(hand: str, *, j_is_joker: bool) -> list[int]:
    # lists use lexicographic ordering when compared against each other,
    # so we can just use a list of card values as a proxy value when sorting hands
    return [
        card_value(card, j_is_joker=j_is_joker)
        for card in hand
    ]


def read_input() -> Input:
    with open(INPUT_FILE_PATH, "r", encoding="utf-8") as f:
        split_lines = (
            line.split()
            for line_ in f.readlines()
            if (line := line_.strip()) != ""
        )
        return [
            (hand, int(bet))
            for hand, bet in split_lines
        ]


def solve(input_: Input, *, j_is_joker: bool) -> int:
    # put a proxy value at the start of each row so the rows can be sorted correctly later
    hands_with_keys = [
        (hand_sorting_key(hand, j_is_joker=j_is_joker), hand, bet)
        for hand, bet in input_
    ]
    # sort hands into buckets by HandType
    get_hand_type = HandType.from_hand_with_jokers if j_is_joker else HandType.from_hand
    hands_grouped_by_type = defaultdict(list)
    for key_hand_bet in hands_with_keys:
        hand_type = get_hand_type(key_hand_bet[1])
        hands_grouped_by_type[hand_type].append(key_hand_bet)
    # sort the hands of each bucket, then concatenate the buckets in order of hand type value
    overall_sorting = [
        key_hand_bet
        for hand_type in HAND_TYPE_ORDER  # outer loop
        for key_hand_bet in sorted(hands_grouped_by_type[hand_type])
    ]
    # calculate the winnings of each hand and add it all up
    total_winnings = sum(
        rank * bet
        for rank, (_, __, bet) in enumerate(overall_sorting, start=1)
    )
    return total_winnings


def main():
    input_ = read_input()
    answer = solve(input_, j_is_joker=False)
    pprint(answer)
    answer = solve(input_, j_is_joker=True)
    pprint(answer)


if __name__ == "__main__":
    main()
