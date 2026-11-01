"""
bharat_business/tests/test_formatting.py

Unit tests for formatting utilities.
Run with: bench run-tests --app bharat_business --module bharat_business.tests.test_formatting
"""

import unittest

from bharat_business.utils.formatting import format_gst_number, format_inr, format_phone_india


class TestFormatINR(unittest.TestCase):

    def test_basic(self):
        self.assertEqual(format_inr(1234567.50), "₹12,34,567.50")

    def test_below_1000(self):
        self.assertEqual(format_inr(999), "₹999.00")

    def test_no_symbol(self):
        self.assertEqual(format_inr(1234567.50, show_symbol=False), "12,34,567.50")

    def test_negative(self):
        self.assertIn("-", format_inr(-500))

    def test_zero(self):
        self.assertEqual(format_inr(0), "₹0.00")

    def test_one_lakh(self):
        self.assertEqual(format_inr(100000), "₹1,00,000.00")

    def test_one_crore(self):
        self.assertEqual(format_inr(10000000), "₹1,00,00,000.00")

    def test_none_returns_empty(self):
        self.assertEqual(format_inr(None), "")


class TestFormatGST(unittest.TestCase):

    def test_valid_gstin(self):
        result = format_gst_number("22AAAAA0000A1Z5")
        self.assertEqual(result, "22 AAAAA0000A 1 Z 5")

    def test_lowercase_normalised(self):
        result = format_gst_number("22aaaaa0000a1z5")
        self.assertEqual(result, "22 AAAAA0000A 1 Z 5")

    def test_invalid_length(self):
        self.assertEqual(format_gst_number("123"), "123")

    def test_none(self):
        self.assertEqual(format_gst_number(None), "")


class TestFormatPhone(unittest.TestCase):

    def test_10_digit(self):
        self.assertEqual(format_phone_india("9876543210"), "+91-98765-43210")

    def test_with_country_code(self):
        self.assertEqual(format_phone_india("919876543210"), "+91-98765-43210")

    def test_empty(self):
        self.assertEqual(format_phone_india(""), "")


if __name__ == "__main__":
    unittest.main()
