"""
bharat_business/bharat_business_setup/page/bb_onboarding/bb_onboarding.py

Server-side controller for the onboarding wizard Frappe Page.
The page itself is a single-page JavaScript application; this file
only exposes the whitelisted API endpoints it calls.
"""

import frappe
from bharat_business.setup.onboarding_service import provision_from_wizard


@frappe.whitelist()
def get_wizard_state():
    """
    Return the current wizard state for the logged-in user's company.
    Creates a new BB Onboarding Wizard document if one doesn't exist yet.
    """
    frappe.only_for(["Bharat Business Owner", "System Manager", "Administrator"])

    default_company = frappe.defaults.get_user_default("Company")

    if not default_company:
        return {"state": "no_company", "wizard_name": None, "current_step": 1}

    wizard_name = frappe.db.get_value("BB Onboarding Wizard", {"company": default_company}, "name")

    if not wizard_name:
        # Create a fresh wizard for this company
        wizard = frappe.get_doc(
            {
                "doctype": "BB Onboarding Wizard",
                "company": default_company,
                "current_step": 1,
            }
        )
        wizard.insert(ignore_permissions=True)
        frappe.db.commit()
        wizard_name = wizard.name

    wizard_doc = frappe.get_doc("BB Onboarding Wizard", wizard_name)
    return {
        "state": "complete" if wizard_doc.is_complete else "in_progress",
        "wizard_name": wizard_name,
        "current_step": wizard_doc.current_step or 1,
        "is_complete": bool(wizard_doc.is_complete),
    }


@frappe.whitelist()
def save_wizard_step(wizard_name: str, step: int, data: str):
    """
    Save data for a single wizard step.
    `data` is a JSON string from the front-end.
    """
    import json
    frappe.only_for(["Bharat Business Owner", "System Manager", "Administrator"])
    wizard = frappe.get_doc("BB Onboarding Wizard", wizard_name)
    return wizard.save_step(int(step), json.loads(data))


@frappe.whitelist()
def complete_onboarding(wizard_name: str):
    """
    Provision all ERPNext documents from wizard data.
    Called after the final wizard step is confirmed by the user.
    """
    frappe.only_for(["Bharat Business Owner", "System Manager", "Administrator"])
    return provision_from_wizard(wizard_name)
