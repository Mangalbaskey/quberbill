"""bharat_business/bharat_business_setup/doctype/bb_branch/bb_branch.py"""

import frappe
from frappe import _
from frappe.model.document import Document


class BBBranch(Document):

    def validate(self):
        self._validate_pincode()
        self._validate_head_office_uniqueness()

    def _validate_pincode(self):
        if self.pincode and not self.pincode.isdigit():
            frappe.throw(_("PIN Code must contain only digits."))
        if self.pincode and len(self.pincode) != 6:
            frappe.throw(_("PIN Code must be exactly 6 digits."))

    def _validate_head_office_uniqueness(self):
        """Only one branch per company can be the head office."""
        if self.is_head_office:
            existing = frappe.db.get_value(
                "BB Branch",
                {"company": self.company, "is_head_office": 1, "name": ["!=", self.name]},
                "name",
            )
            if existing:
                frappe.throw(
                    _("Branch {0} is already marked as Head Office for {1}.").format(
                        existing, self.company
                    )
                )
