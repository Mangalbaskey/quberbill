"""
bharat_business/bharat_business_setup/doctype/bb_onboarding_wizard/bb_onboarding_wizard.py

Controller for the onboarding wizard state tracker.
The actual wizard UI is the Frappe Page `bb_onboarding`.
This DocType stores progress so the wizard can resume after page refresh.
"""

import json

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import now_datetime


class BBOnboardingWizard(Document):

    def validate(self):
        if self.current_step and (self.current_step < 1 or self.current_step > 11):
            frappe.throw(_("Wizard step must be between 1 and 11."))

    @frappe.whitelist()
    def save_step(self, step: int, data: dict):
        """
        Called by the front-end wizard after each step is completed.
        Merges new step data into the existing JSON blob and advances
        current_step.

        :param step: Step number just completed (1–11)
        :param data: Dict of field values collected in that step
        """
        existing = {}
        if self.step_data:
            try:
                existing = json.loads(self.step_data)
            except json.JSONDecodeError:
                existing = {}

        existing[f"step_{step}"] = data
        self.step_data = json.dumps(existing, ensure_ascii=False, indent=2)
        self.current_step = step + 1
        self.save(ignore_permissions=False)
        return {"next_step": self.current_step}

    @frappe.whitelist()
    def complete_wizard(self):
        """
        Mark wizard as complete. Called by OnboardingService after all
        ERPNext documents have been successfully created.
        """
        self.is_complete = 1
        self.completed_at = now_datetime()
        self.save(ignore_permissions=False)

        # Mark the linked Business Profile as complete
        if self.business_profile:
            frappe.db.set_value(
                "BB Business Profile",
                self.business_profile,
                "onboarding_complete",
                1,
            )
        return {"status": "complete"}
