import unittest

from lambda_src.calculator_core import CalculatorError, calculate_expression, extract_expression


class CalculatorCoreTests(unittest.TestCase):
    def test_calculates_parentheses(self):
        self.assertEqual(calculate_expression("12 * (7 + 5)"), "144")

    def test_extracts_expression_from_text(self):
        self.assertEqual(extract_expression("please calculate 9 / 3"), "9 / 3")

    def test_rejects_function_calls(self):
        with self.assertRaises(CalculatorError):
            calculate_expression("__import__('os').system('whoami')")

    def test_rejects_large_exponent(self):
        with self.assertRaises(CalculatorError):
            calculate_expression("2 ** 999")


if __name__ == "__main__":
    unittest.main()

