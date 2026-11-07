"""
bharat_business/setup/auth_routing.py

Internal authentication and routing separation.
Ensures business clients/customers are routed to their store POS/workspace,
and strictly kept out of platform administration.
"""

import frappe


def on_login(login_manager):
    """
    Hook executed immediately after successful login.
    Routes business clients to their store workspace and separates them
    from platform administration.
    """
    user = frappe.session.user
    if not user or user in ("Guest", "Administrator"):
        return

    roles = frappe.get_roles(user)
    bb_roles = [r for r in roles if r.startswith("Bharat Business")]

    if not bb_roles:
        return

    # Look up the user's assigned company from User Permission
    company = frappe.db.get_value(
        "User Permission",
        {"user": user, "allow": "Company"},
        "for_value"
    )

    if not company:
        # Check if they created a business profile
        company = frappe.db.get_value("BB Business Profile", {"created_by": user}, "company")

    if not company:
        # User has not created a business yet, send to onboarding
        frappe.local.response["home_page"] = "/app/bb_onboarding"
        return

    # Check onboarding completion status
    is_complete = frappe.db.get_value("BB Business Profile", {"company": company}, "onboarding_complete")

    if not is_complete:
        frappe.local.response["home_page"] = "/app/bb_onboarding"
    else:
        # Route directly to their fast billing / POS interface
        frappe.local.response["home_page"] = "/app/bb-pos"
