from math import log10
from itertools import permutations
import pdb


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


def magic(integer_spell: int):
    spell_traits = set()
    if integer_spell % 2 == 0:
        spell_traits.add("addition")
        if integer_spell % 5 == 0:
            spell_traits.add("confusion")
    if integer_spell % 2 != 0:
        spell_traits.add("subtraction")
        if integer_spell % 1001 == 0:
            spell_traits.add("temptation")
    if is_vampire_number(integer_spell):
        spell_traits.add("vampire")
    return spell_traits
