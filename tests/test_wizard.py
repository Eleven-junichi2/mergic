import unittest

from mergic import wizard


class TestWizard(unittest.TestCase):
    def test_magic(self):
        self.assertSetEqual(
            set(
                [
                    "addition",
                ]
            ),
            wizard.magic(2),
        )
        self.assertSetEqual(
            set(
                [
                    "subtraction",
                ]
            ),
            wizard.magic(1),
        )
        self.assertSetEqual(
            set(["subtraction", "temptation"]),
            wizard.magic(1001),
        )
        self.assertSetEqual(
            set(["addition", "confusion"]),
            wizard.magic(10),
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
        non_vampiric_numbers = [1, 123, 1590]
        for testcase in vampire_numbers:
            self.assertTrue(
                wizard.is_vampire_number(testcase), f"testcase num: {testcase}"
            )
        for testcase in non_vampiric_numbers:
            self.assertFalse(
                wizard.is_vampire_number(testcase), f"testcase num: {testcase}"
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
            58
        ]
        for testcase, errorcase  in zip(strobogrammatic_numbers, non_strobogrammatic_numbers):
            self.assertTrue(
                wizard.is_strobogrammatic_number(testcase), f"testcase num: {testcase}"
            )
            self.assertFalse(
                wizard.is_strobogrammatic_number(errorcase), f"errorcase num: {errorcase}"
            )
