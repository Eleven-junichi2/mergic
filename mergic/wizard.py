from collections import deque
from dataclasses import dataclass, field
from enum import Enum, StrEnum, auto
from math import log10
from itertools import permutations, islice, chain
import math
import os
from typing import Callable, Iterable, TypedDict, Unpack
import time
import random
import functools
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


def measure_time_performance(func: Callable):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.perf_counter_ns()
        print(f"run Func {func.__name__}")
        result = func(*args, **kwargs)
        end_time = time.perf_counter_ns()
        time.perf_counter()
        print(
            f"Func {func.__name__} took {(end_time - start_time)/(10**9):.9f} seconds, result={result}"
        )
        return result

    return wrapper


# @measure_time_performance
def is_prime_number(number: int):
    return sympy.isprime(number)
    # if number < 2:
    #     return False
    # found_primes = [True] * (number+1)
    # found_primes[0] = found_primes[1] = False
    # if number == 0:
    #     return False
    # for num in range(2 ** 2, number + 1):
    #     print("\033[A", num)
    #     if found_primes[num]:
    #         for i in range(num * num, number + 1, num):
    #             # print("i", i, end=" compromise!\n")
    #             # print("i", i)
    #             # if number % i == 0:
    #             found_primes[i] = False
    # return found_primes[number]


def join_digits(digits: Iterable):
    joined = 0
    for digit, num in enumerate(digits):
        joined += num * 10**digit
    return joined


# @measure_time_performance
async def concurrently_join_digits(*digits_iter: Unpack[Iterable]):
    loop = asyncio.get_running_loop()
    with concurrent.futures.ThreadPoolExecutor() as pool:
        return await asyncio.gather(
            # pool.map(join_digits, digits_iter)
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


# @measure_time_performance
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
        # print(digits_pattern)
        left_digits = digits_pattern[: digit_length // 2]
        right_digits = digits_pattern[digit_length // 2 :]
        if left_digits[-1] + right_digits[-1] == 0:
            continue
        left, right = asyncio.run(concurrently_join_digits(left_digits, right_digits))
        if left * right == number:
            return True


# @measure_time_performance
def is_vampire_number(number: int) -> bool:
    """TODO: improve algorithm"""
    digits, digit_length = split_number_into_digits(number)
    if digit_length % 2 != 0:
        return False
    chunks = split_into_chunks(set(permutations(digits)), os.cpu_count() // 2)
    with concurrent.futures.ProcessPoolExecutor() as executor:
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
    # return result
    # for chunk in chunks:
    #     for digits_pattern in chunk:
    #         print(digits_pattern)
    #         left_digits = digits_pattern[: digit_length // 2]
    #         right_digits = digits_pattern[digit_length // 2 :]
    #         if left_digits[-1] + right_digits[-1] == 0:
    #             continue
    #         left, right = asyncio.run(
    #             concurrently_join_digits(left_digits, right_digits)
    #         )
    #         if left * right == number:
    #             return True
    return False


# @measure_time_performance
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


class IntTypeBitmaskMarker(Enum):
    ODD = 0b00001
    EVEN = 0b00010
    PRIME = 0b00100
    VAMPIRE = 0b01000
    STROBOGRAMMATIC = 0b10000


# @measure_time_performance
def generate_magic(integer_spell: int, strength: int) -> Magic:
    if integer_spell > 10**9:
        raise ValueError("integer_spell is too large")
    found_inttype = 0
    magic = Magic(set(), set(), 0)
    magic.strength = strength

    async def async_int_type_check(integer_spell: int):
        loop = asyncio.get_running_loop()
        with concurrent.futures.ThreadPoolExecutor() as pool:
            task_prime = loop.run_in_executor(pool, is_prime_number, integer_spell)
            task_vampire = loop.run_in_executor(pool, is_vampire_number, integer_spell)
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
        magic.traits.add("addition")
        if integer_spell < 0:
            magic.alchemical_elements.add(AlchemicalElement.COLD)
        if integer_spell % 5 == 0:
            magic.traits.add("confusion")
    if integer_spell % 2 != 0:
        found_inttype |= IntTypeBitmaskMarker.ODD.value
        magic.traits.add("subtraction")
        if integer_spell < 0:
            magic.alchemical_elements.add(AlchemicalElement.HEAT)
        if integer_spell % 1001 == 0:
            magic.traits.add("temptation")
    if found_inttype & IntTypeBitmaskMarker.VAMPIRE.value:
        magic.traits.add("vampire")
    if found_inttype & IntTypeBitmaskMarker.STROBOGRAMMATIC.value:
        magic.traits.add("drowsiness")
    if (
        found_inttype
        & IntTypeBitmaskMarker.STROBOGRAMMATIC.value
        & IntTypeBitmaskMarker.PRIME.value
    ):
        magic.traits.add("sleep")
    return magic


def auto_name(magic: Magic, language_code="en"):
    name = ""
    element_or_trait_names = [
        str(element) for element in magic.alchemical_elements
    ] + list(magic.traits)
    element_or_trait_names_size = len(element_or_trait_names)
    random.shuffle(element_or_trait_names)
    # print(element_or_trait_names, "size:", element_or_trait_names_size)
    for i, element_or_trait_name in enumerate(element_or_trait_names):
        # print("name:", element_or_trait_name, "name length:", len(element_or_trait_name))
        start = i * (len(element_or_trait_name) // element_or_trait_names_size)
        end_ = (i + 1) * (len(element_or_trait_name) // element_or_trait_names_size)
        # print(start, "/", end_)
        part = element_or_trait_name[start:end_]
        # print(part)
        name += part
    if language_code == "en":
        pass
    elif language_code == "ja":
        name = jaconv.alphabet2kana(name)
        name = name.replace("っっ", "")
        if name[0] == "っ":
            name = name[1:]
        if name[-1] == "っ":
            name[-1] == "ー"
        name = jaconv.hira2kata(name)
    else:
        raise NotImplementedError(f"{language_code} name is not supported.")
    return name


def playground_cli():
    print("Wizard's playground")
    int_spell = int(input("integer spell: "))
    strength = int(input("strength: "))
    magic = generate_magic(int_spell, strength)
    print(magic.traits)
    print(magic.alchemical_elements)
    print(magic.strength)
    for language_code in ("en", "ja"):
        print(
            f"auto-generated name({language_code}): ", auto_name(magic, language_code)
        )


if __name__ == "__main__":
    print(generate_magic(9_9999_1111, 0))
    # print(is_prime_number(1919111261))
    # playground_cli()
