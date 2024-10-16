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
