from dataclasses import dataclass, field
from enum import Enum, auto
from math import log10
from itertools import permutations
from typing import TypedDict


class AlchemicalElement(Enum):
    VOID = auto()
    HEAT = auto()
    COLD = auto()
    LIGHT = auto()
    DARK = auto()


@dataclass
class Magic:
    alchemical_elements: set[AlchemicalElement]
    traits: set
    strength: int


@dataclass
class Mana:
    max_: int
    current: int = field(init=False)

    def __post_init__(self):
        self.current = self.max_


class SpellRecord(TypedDict):
    ingeger_spell: int
    default_strength: int
    memo: str


class SpellDatabase(TypedDict):
    name: dict[str, SpellRecord]


def is_vampire_number(number: int) -> bool:
    """TODO: improve algorithm"""
    digit_length = int(log10(number)) + 1
    if digit_length % 2 != 0:
        return False
    digit_list = []
    for digit in range(digit_length):
        digit_list.append((number // 10**digit) % 10)
    for digits_pattern in permutations(digit_list):
        left_digits = digits_pattern[: digit_length // 2]
        right_digits = digits_pattern[digit_length // 2 :]
        left = 0
        right = 0
        is_left_end_zero = False
        is_right_end_zero = False
        for digit, num in enumerate(reversed(left_digits)):
            if digit == 0 and num == 0:
                is_left_end_zero = True
            left += num * 10**digit
        for digit, num in enumerate(reversed(right_digits)):
            right += num * 10**digit
            if digit == 0 and num == 0:
                is_left_end_zero = False
        if is_left_end_zero and is_right_end_zero:
            continue
        else:
            if left * right == number:
                return True
    return False


def is_strobogrammatic_number(
    number: int, symmetrical_nums=(0, 1, 8), symmetrical_pairs=((6, 9),)
):
    """
    TODO:
    - Stop the iteration when the middle digit is reached, as the check is complete.
    - Improve the algorithm
    """
    if number == 0:
        digit_length = 1
    else:
        digit_length = int(log10(number)) + 1
    digit_list = []
    for digit in range(digit_length):
        digit_list.append((number // 10**digit) % 10)

    for i, number in enumerate(digit_list):
        symmetrical_pair_found = False
        if number in symmetrical_nums:
            if digit_list[-i - 1] == number:
                symmetrical_pair_found = True
                continue
            else:
                return False
        for symmetrical_pair in symmetrical_pairs:
            if number == symmetrical_pair[0]:
                if digit_list[-i - 1] == symmetrical_pair[1]:
                    symmetrical_pair_found = True
                    break
                else:
                    return False
            elif number == symmetrical_pair[1]:
                if digit_list[-i - 1] == symmetrical_pair[0]:
                    symmetrical_pair_found = True
                    break
                else:
                    return False
        if not symmetrical_pair_found:
            return False
    return True


def generate_magic(integer_spell: int, strength: int) -> Magic:
    magic = Magic(AlchemicalElement.VOID, set(), 0)
    if integer_spell > 0:
        magic.alchemical_elements.add(AlchemicalElement.LIGHT)
    if integer_spell < 0:
        magic.alchemical_elements.add(AlchemicalElement.DARK)
    if integer_spell % 2 == 0:
        magic.traits.add("addition")
        if integer_spell > 0:
            magic.alchemical_elements.add(AlchemicalElement.HEAT)
        if integer_spell < 0:
            magic.alchemical_elements.add(AlchemicalElement.COLD)
        if integer_spell % 5 == 0:
            magic.traits.add("confusion")
    if integer_spell % 2 != 0:
        magic.traits.add("subtraction")
        if integer_spell > 0:
            magic.alchemical_elements.add(AlchemicalElement.COLD)
        if integer_spell < 0:
            magic.alchemical_elements.add(AlchemicalElement.HEAT)
        if integer_spell % 1001 == 0:
            magic.traits.add("temptation")
    if is_vampire_number(integer_spell):
        magic.traits.add("vampire")
    if is_strobogrammatic_number(integer_spell):
        magic.traits.add("drowsiness")
    if integer_spell == 0:
        magic.alchemical_elements.add(AlchemicalElement.VOID)
    magic.strength = strength
    return magic
