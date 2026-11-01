"""
bharat_business/tests/test_bb_business_profile.py

Integration tests for BB Business Profile DocType.
Requires a running Frappe site with bharat_business installed.

Run with: bench run-tests --app bharat_business --module bharat_business.tests.test_bb_business_profile
"""

import unittest
import frappe
from frappe.exceptions import ValidationError


class TestBBBusinessProfile(unittest.TestCase):

    def setUp(self):
        self.test_company = frappe.db.get_value("Company", {"country": "India"}, "name")
        if not self.test_company:
            # Create a test company for tests
            company = frappe.get_doc(
                {
                    "doctype": "Company",
                    "company_name": "_Test Bharat Co",
                    "abbr": "_TBC",
                    "default_currency": "INR",
                    "country": "India",
                }
            )
            company.insert(ignore_permissions=True)
            self.test_company = company.name

    def _make_profile(self, **kwargs):
        defaults = {
            "doctype": "BB Business Profile",
            "profile_name": f"Test Profile {frappe.utils.now()}",
            "company": self.test_company,
            "business_type": "retail",
            "gst_category": "Unregistered",
        }
        defaults.update(kwargs)
        return frappe.get_doc(defaults)

    def test_unregistered_no_gstin_required(self):
        """Unregistered businesses must not require GSTIN."""
        profile = self._make_profile(gst_category="Unregistered")
        try:
            profile.validate()  # Should not raise
        except Exception as e:
            self.fail(f"validate() raised unexpectedly: {e}")

    def test_registered_requires_gstin(self):
        """Registered Regular without GSTIN must fail validation."""
        profile = self._make_profile(gst_category="Registered Regular", gstin="")
        with self.assertRaises(ValidationError):
            profile.validate()

    def test_invalid_gstin_format(self):
        """Invalid GSTIN format must fail validation."""
        profile = self._make_profile(
            gst_category="Registered Regular",
            gstin="INVALID_GSTIN_FORMAT",
        )
        with self.assertRaises(ValidationError):
            profile.validate()

    def test_valid_gstin_accepted(self):
        """A correctly formatted GSTIN must pass validation."""
        profile = self._make_profile(
            gst_category="Registered Regular",
            gstin="22AAAAA0000A1Z5",  # Standard test GSTIN format
        )
        try:
            profile.validate()
        except ValidationError as e:
            self.fail(f"validate() raised on valid GSTIN: {e}")

    def test_gstin_uppercased(self):
        """GSTIN should be uppercased during validation."""
        profile = self._make_profile(
            gst_category="Registered Regular",
            gstin="22aaaaa0000a1z5",
        )
        profile.validate()
        self.assertEqual(profile.gstin, "22AAAAA0000A1Z5")

    def test_get_active_modules_retail(self):
        """Retail profile with inventory + POS must return correct modules."""
        profile = self._make_profile(
            business_type="retail",
            enable_inventory=1,
            enable_pos=1,
            enable_purchase=1,
        )
        modules = profile.get_active_modules()
        self.assertIn("billing", modules)
        self.assertIn("inventory", modules)
        self.assertIn("pos", modules)
        self.assertNotIn("manufacturing", modules)

    def tearDown(self):
        frappe.db.rollback()
