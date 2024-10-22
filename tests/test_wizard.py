import unittest

from mergic import wizard
from mergic.wizard import SpellTrait
from mergic.status import StatusEffect, StatusEffectContent, OwnedStatusEffects


class TestWizard(unittest.TestCase):
    def test_magic(self):
        with self.assertRaises(ValueError):
            wizard.spell_factory.generate(10_000_000_000, 1)
        self.assertSetEqual(
            set(
                [
                    SpellTrait.HEAL,
                ]
            ),
            wizard.spell_factory.generate(2, 1).traits,
        )
        self.assertSetEqual(
            set([SpellTrait.DAMAGE, SpellTrait.TEMPTATION, SpellTrait.DROWSINESS]),
            wizard.spell_factory.generate(1001, 1).traits,
        )
        self.assertSetEqual(
            set([SpellTrait.HEAL, SpellTrait.CONFUSION]),
            wizard.spell_factory.generate(10, 1).traits,
        )
        print(wizard.spell_factory.generate(1, 1).traits)
        self.assertSetEqual(
            {
                SpellTrait.DROWSINESS,
                SpellTrait.DAMAGE,
            },
            wizard.spell_factory.generate(1, 1).traits,
        )

    def test_vampire_number(self):
        vampire_numbers = [
            1260,
            1395,
            1435,
            1530,
            1827,
            2187,
            6880,
            102510,
            104260,
            105210,
            105264,
            105750,
            108135,
            110758,
            115672,
            116725,
            117067,
            118440,
            120600,
            123354,
            124483,
            125248,
            125433,
            125460,
            125500,
        ]
        non_vampiric_numbers = [0, 1, 123, 1590]
        for testcase in vampire_numbers:
            self.assertTrue(
                wizard.is_vampire_number(testcase), f"testcase num: {testcase}"
            )
        for testcase in non_vampiric_numbers:
            self.assertFalse(
                wizard.is_vampire_number(testcase), f"testcase num: {testcase}"
            )

    def test_prime_number(self):
        non_prime_numbers = [0, 6, 10, 8]
        for testcase in non_prime_numbers:
            self.assertFalse(
                wizard.is_prime_number(testcase), f"testcase num: {testcase}"
            )
        prime_numbers = [
            2,
            3,
            5,
            7,
            11,
            13,
            17,
            19,
            23,
            29,
            31,
            37,
            41,
            43,
            47,
            53,
            59,
            61,
            67,
            71,
            73,
            79,
            83,
            89,
            97,
        ]
        for testcase in prime_numbers:
            self.assertTrue(
                wizard.is_prime_number(testcase), f"testcase num: {testcase}"
            )

    def test_strobogrammatic_number(self):
        strobogrammatic_numbers = [
            0,
            1,
            8,
            11,
            69,
            88,
            96,
            101,
            111,
            181,
            609,
            619,
            689,
            808,
            818,
            888,
            906,
            916,
            986,
            1001,
            1111,
            1691,
            1881,
            1961,
            6009,
            6119,
            6699,
            6889,
            6969,
            8008,
            8118,
            8698,
            8888,
            8968,
            9006,
            9116,
            9696,
            9886,
            9966,
        ]
        non_strobogrammatic_numbers = [
            2,
            3,
            4,
            5,
            7,
            9,
            12,
            13,
            14,
            15,
            16,
            17,
            18,
            20,
            21,
            22,
            23,
            24,
            25,
            26,
            27,
            28,
            29,
            30,
            31,
            32,
            33,
            34,
            35,
            36,
            37,
            38,
            39,
            40,
            41,
            42,
            43,
            44,
            45,
            46,
            47,
            48,
            49,
            50,
            51,
            52,
            53,
            54,
            55,
            56,
            57,
            58,
        ]
        for testcase, errorcase in zip(
            strobogrammatic_numbers, non_strobogrammatic_numbers
        ):
            self.assertTrue(
                wizard.is_strobogrammatic_number(testcase), f"testcase num: {testcase}"
            )
            self.assertFalse(
                wizard.is_strobogrammatic_number(errorcase),
                f"errorcase num: {errorcase}",
            )

    def test_split_into_chunks(self):
        collection_ = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        self.assertEqual(
            [[1, 2, 3, 4, 5], [6, 7, 8, 9, 10]],
            [list(chunk) for chunk in wizard.split_into_chunks(collection_, 2)],
        )
        collection_ = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
        self.assertEqual(
            [[1, 2, 3, 4, 5], [6, 7, 8, 9, 10, 11]],
            [list(chunk) for chunk in wizard.split_into_chunks(collection_, 2)],
        )
        collection_ = [1, 2, 3, 4, 5, 6, 7]
        self.assertEqual(
            [[1, 2], [3, 4], [5, 6, 7]],
            [list(chunk) for chunk in wizard.split_into_chunks(collection_, 3)],
        )

    def test_split_number_into_digits(self):
        self.assertEqual(
            [[1, 2, 3], 3],
            list(wizard.split_number_into_digits(123)),
        )
        self.assertEqual(
            [[1, 0, 2, 3, 4], 5],
            list(wizard.split_number_into_digits(10234)),
        )
        self.assertEqual(
            [[1, 2, 3, 4, 5, 6, 7], 7],
            list(wizard.split_number_into_digits(1234567)),
        )


class TestStatusEffect(unittest.TestCase):
    def test_owned_status_effect(self):
        status_effects = OwnedStatusEffects()
        status_effects[StatusEffect.CONFUSING].append(
            StatusEffectContent(turns_remaining=1)
        )
