from dataclasses import dataclass
from enum import Flag, StrEnum, auto
from math import log10
from itertools import permutations, islice
from typing import Iterable, Optional, Unpack
import random
import asyncio
import concurrent.futures

import jaconv
import sympy


class AlchemicalElement(StrEnum):
    VOID = auto()
    HEAT = auto()
    COLD = auto()
    LIGHT = auto()
    DARK = auto()


class SpellTrait(StrEnum):
    HEAL = auto()
    DAMAGE = auto()
    CONFUSION = auto()
    TEMPTATION = auto()
    VAMPIRE = auto()
    DROWSINESS = auto()
    SLEEP = auto()
    RANDOM_ELEMENTS = auto()
    STUN = auto()
    DISPEL = auto()
    PURIFY = auto()
    POISON = auto()


@dataclass
class Magic:
    alchemical_elements: set[AlchemicalElement]
    traits: set[SpellTrait]
    strength: int
    generator_integer: Optional[int] = None


@dataclass
class SpellRecord:
    magic: Magic
    memo: str = ""


def is_prime_number(number: int):
    return sympy.isprime(number)


def join_digits(digits: Iterable):
    joined = 0
    for digit, num in enumerate(digits):
        joined += num * 10**digit
    return joined


async def concurrently_join_digits(*digits_iter: Unpack[Iterable]):
    loop = asyncio.get_running_loop()
    with concurrent.futures.ThreadPoolExecutor() as pool:
        return await asyncio.gather(
            *[loop.run_in_executor(pool, join_digits, digits) for digits in digits_iter]
        )


def split_into_chunks(
    collection_: Iterable, num_chunks: int, end_with_fraction: bool = True
):
    """Split given collection into chunks.
    Given a number of chunks that is not divisible by the size of the given collection,
    ignore the remainder and split up to the divisible size;
    if end_with_fraction is True, the ignored part is included in the last chunk and returned."""
    collection_size = len(collection_)
    chunk_size = collection_size // num_chunks
    return list(
        [
            list(islice(collection_, chunk_size * i, chunk_size * (i + 1)))
            if (not i + 1 == num_chunks) and end_with_fraction
            else list(
                islice(
                    collection_,
                    chunk_size * i,
                    chunk_size * (i + 1) + collection_size % num_chunks,
                )
            )
            for i in range(num_chunks)
        ]
    )


def split_number_into_digits(number: int):
    """Splits a number into its individual digits. Returns the digits and the length of the digits."""
    if number == 0:
        return [number, 1]
    digit_length = int(log10(number)) + 1
    return list(
        reversed([(number // 10**digit % 10) for digit in range(digit_length)])
    ), digit_length


def _verify_is_digit_split_product_vampire_number_fangs(
    number, digits_list, digit_length
):
    for digits_pattern in digits_list:
        left_digits = digits_pattern[: digit_length // 2]
        right_digits = digits_pattern[digit_length // 2 :]
        if left_digits[-1] + right_digits[-1] == 0:
            continue
        left, right = asyncio.run(concurrently_join_digits(left_digits, right_digits))
        if left * right == number:
            return True


def is_vampire_number(number: int) -> bool:
    """TODO: improve algorithm"""
    digits, digit_length = split_number_into_digits(number)
    if digit_length % 2 != 0:
        return False
    chunks = split_into_chunks(set(permutations(digits)), 2)
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = [
            executor.submit(
                _verify_is_digit_split_product_vampire_number_fangs,
                number,
                chunk,
                digit_length,
            )
            for chunk in chunks
        ]
        results = [
            future.result() for future in concurrent.futures.as_completed(futures)
        ]
    return any(results)


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


class IntTypeBitmaskMarker(Flag):
    ODD = auto()
    EVEN = auto()
    PRIME = auto()
    VAMPIRE = auto()
    STROBOGRAMMATIC = auto()


class spell_factory:
    integer_spell_max = 10**9

    @classmethod
    def generate(cls, integer_spell: int, strength: int) -> Magic:
        if integer_spell > cls.integer_spell_max:
            raise ValueError(
                f"integer_spell is too large. (max: {cls.integer_spell_max})"
            )
        found_inttype = 0
        magic = Magic(set(), set(), strength=strength, generator_integer=integer_spell)

        async def async_int_type_check(integer_spell: int):
            loop = asyncio.get_running_loop()
            with concurrent.futures.ThreadPoolExecutor() as pool:
                task_prime = loop.run_in_executor(pool, is_prime_number, integer_spell)
                task_vampire = loop.run_in_executor(
                    pool, is_vampire_number, integer_spell
                )
                task_strobogrammatic = loop.run_in_executor(
                    pool, is_strobogrammatic_number, integer_spell
                )
                is_prime = await task_prime
                is_vampire = await task_vampire
                is_strobogrammatic = await task_strobogrammatic
                return (
                    IntTypeBitmaskMarker.PRIME.value * is_prime
                    | IntTypeBitmaskMarker.VAMPIRE.value * is_vampire
                    | IntTypeBitmaskMarker.STROBOGRAMMATIC.value * is_strobogrammatic
                )

        found_inttype = asyncio.run(
            async_int_type_check(integer_spell),
        )
        if integer_spell == 0:
            magic.alchemical_elements.add(AlchemicalElement.VOID)
        if integer_spell > 0:
            magic.alchemical_elements.add(AlchemicalElement.LIGHT)
        if integer_spell < 0:
            magic.alchemical_elements.add(AlchemicalElement.DARK)
        if integer_spell % 2 == 0:
            found_inttype |= IntTypeBitmaskMarker.EVEN.value
            magic.traits.add(SpellTrait.HEAL)
            if integer_spell < 0:
                magic.alchemical_elements.add(AlchemicalElement.COLD)
            if integer_spell % 5 == 0:
                magic.traits.add(SpellTrait.CONFUSION)
        if integer_spell % 2 != 0:
            found_inttype |= IntTypeBitmaskMarker.ODD.value
            magic.traits.add(SpellTrait.DAMAGE)
            if integer_spell < 0:
                magic.alchemical_elements.add(AlchemicalElement.HEAT)
            if integer_spell % 1001 == 0:
                magic.traits.add(SpellTrait.TEMPTATION)
        if found_inttype & IntTypeBitmaskMarker.VAMPIRE.value:
            magic.traits.add(SpellTrait.VAMPIRE)
        if found_inttype & IntTypeBitmaskMarker.STROBOGRAMMATIC.value:
            magic.traits.add(SpellTrait.DROWSINESS)
        if (
            found_inttype
            & IntTypeBitmaskMarker.STROBOGRAMMATIC.value
            & IntTypeBitmaskMarker.PRIME.value
        ):
            magic.traits.add(SpellTrait.SLEEP)
        return magic


def auto_name(magic: Magic, language_code="en"):
    name = ""
    element_or_trait_names = [str(element) for element in magic.alchemical_elements] + [
        str(trait) for trait in magic.traits
    ]
    """Generate string based on the given magic's elements and traits."""
    element_or_trait_names_size = len(element_or_trait_names)
    random.shuffle(element_or_trait_names)
    for i, element_or_trait_name in enumerate(element_or_trait_names):
        start = i * (len(element_or_trait_name) // element_or_trait_names_size)
        end_ = (i + 1) * (len(element_or_trait_name) // element_or_trait_names_size)
        part = element_or_trait_name[start:end_]
        name += part
    if language_code == "en":
        pass
    elif language_code == "ja":
        name = jaconv.alphabet2kana(name)
        name = name.replace("っっ", "")
        if name[0] == "っ":
            name = name[1:]
        if name[-1] == "っ":
            name = name[:-1] + "ー"
        name = jaconv.hira2kata(name)
    else:
        raise NotImplementedError(f"{language_code} name is not supported.")
    return name


def auto_description(magic, language_code="en"):
    description = ""
    if language_code == "en":
        pass
    elif language_code == "ja":
        pass
    else:
        raise NotImplementedError(f"{language_code} description is not supported.")
    return description
