"""
bharat_business/setup/boot.py

Injected into every Frappe boot session via hooks.py `boot_session`.
Loads the BB Business Profile for the current user's company so the
front-end knows which business type is active, which modules to show,
and which language to use.
"""

import frappe


def boot_session(bootinfo):
    """
    Append bharat_business context to the boot payload.

    `bootinfo` is a dict-like object passed to the browser on login.
    Everything added here becomes available as `frappe.boot.bharat_business`
    in client-side JavaScript.
    """
    bb_context = {
        "enabled": False,
        "business_type": None,
        "profile_name": None,
        "enable_inventory": False,
        "onboarding_complete": False,
    }

    try:
        # Only populate if the user has at least one BB role
        user_roles = frappe.get_roles(frappe.session.user)
        bb_roles = {r for r in user_roles if r.startswith("Bharat Business")}

        if bb_roles:
            # Fetch the first BB Business Profile linked to the default company
            default_company = frappe.defaults.get_user_default("Company")
            if default_company:
                profile = frappe.db.get_value(
                    "BB Business Profile",
                    {"company": default_company, "is_active": 1},
                    ["name", "business_type", "enable_inventory", "onboarding_complete"],
                    as_dict=True,
                )
                if profile:
                    bb_context.update(
                        {
                            "enabled": True,
                            "business_type": profile.business_type,
                            "profile_name": profile.name,
                            "enable_inventory": bool(profile.enable_inventory),
                            "onboarding_complete": bool(profile.onboarding_complete),
                        }
                    )
    except Exception:
        # Boot must never fail — log silently
        frappe.log_error(frappe.get_traceback(), "[bharat_business] boot_session error")

    bootinfo["bharat_business"] = bb_context
