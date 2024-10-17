from dataclasses import dataclass
from enum import Enum, auto
from math import log10
from itertools import permutations
import pdb


class AlchemicalElement(Enum):
    VOID = auto()
    HEAT = auto()
    COLD = auto()
    LIGHT = auto()
    DARK = auto()

@dataclass
class Magic:
    alchemical_element: AlchemicalElement
    traits: set
    strength: int


def is_vampire_number(number: int) -> bool:
    # TODO: improve algorithm
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


def generate_magic(integer_spell: int, strength: int):
    magic = Magic(AlchemicalElement.VOID, set(), 0)
    if integer_spell > 0:
        magic.alchemical_element
    if integer_spell % 2 == 0:
        magic.traits.add("addition")
        if integer_spell % 5 == 0:
            magic.traits.add("confusion")
    if integer_spell % 2 != 0:
        magic.traits.add("subtraction")
        if integer_spell % 1001 == 0:
            magic.traits.add("temptation")
    if is_vampire_number(integer_spell):
        magic.traits.add("vampire")
    return magic
