"""
bharat_business/bharat_business_setup/doctype/bb_business_profile/bb_business_profile.py

Controller for BB Business Profile.

Validates GSTIN format, enforces business rule constraints, and ensures that
all ERPNext-linked documents (Company, GST Settings) stay in sync.

IMPORTANT: This controller does NOT touch ERPNext accounting entries directly.
All Company / GST Settings updates go through their respective ERPNext APIs.
"""

import re

import frappe
from frappe import _
from frappe.model.document import Document


# GSTIN format: 2-digit state code + 10-char PAN + 1 entity number + Z + checksum
GSTIN_PATTERN = re.compile(
    r"^[0-3][0-9][A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}$"
)


class BBBusinessProfile(Document):
    # ----- Frappe lifecycle hooks -----

    def validate(self):
        self._validate_gstin()
        self._validate_e_invoice_eligibility()
        self._set_audit_fields()

    def before_save(self):
        self._sync_company_gstin()

    def on_update(self):
        frappe.cache().delete_key(f"bb_profile_{self.company}")

    # ----- Validation helpers -----

    def _validate_gstin(self):
        """Validate GSTIN format for registered businesses."""
        if self.gst_category in ("Registered Regular", "Registered Composition", "SEZ"):
            if not self.gstin:
                frappe.throw(
                    _("GSTIN is required for GST category: {0}").format(self.gst_category),
                    title=_("Missing GSTIN"),
                )
            if not GSTIN_PATTERN.match(self.gstin.upper()):
                frappe.throw(
                    _("Invalid GSTIN format: {0}. Expected format: 22AAAAA0000A1Z5").format(
                        self.gstin
                    ),
                    title=_("Invalid GSTIN"),
                )
            self.gstin = self.gstin.upper()

    def _validate_e_invoice_eligibility(self):
        """
        Warn when e-invoice is enabled but turnover threshold is unclear.
        E-invoice is mandatory for turnover > ₹5 crore (notified threshold).
        """
        if self.enable_e_invoice and (self.annual_turnover_cr or 0) < 5:
            frappe.msgprint(
                _(
                    "E-Invoice is enabled but estimated turnover is below ₹5 crore. "
                    "E-Invoice is mandatory only above the notified threshold. "
                    "Verify with your CA before enabling."
                ),
                title=_("E-Invoice Notice"),
                indicator="orange",
            )

    def _set_audit_fields(self):
        if self.is_new():
            self.created_by = frappe.session.user
        self.modified_by = frappe.session.user

    def _sync_company_gstin(self):
        """
        Sync GSTIN to the Company master if it has changed.
        Uses ERPNext's Company DocType — not direct SQL.
        """
        if not self.gstin or not self.company:
            return
        current_company_gstin = frappe.db.get_value("Company", self.company, "gstin")
        if current_company_gstin != self.gstin:
            frappe.db.set_value("Company", self.company, "gstin", self.gstin)

    # ----- Public API methods -----

    @frappe.whitelist()
    def get_active_modules(self):
        """
        Return the list of active module keys for this business profile.
        Used by the front-end to render the correct workspace.
        """
        modules = ["billing", "customers", "suppliers", "payments", "reports"]
        if self.enable_inventory:
            modules.append("inventory")
        if self.enable_pos:
            modules.append("pos")
        if self.enable_manufacturing:
            modules.append("manufacturing")
        if self.enable_purchase:
            modules.append("purchase")
        return modules
