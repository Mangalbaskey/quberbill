"""
bharat_business/setup/install.py

Called by Frappe after `bench install-app bharat_business` and after every
`bench migrate`. Creates default configuration that must exist before users
can log in.

IMPORTANT: All ERPNext objects (Company, Warehouse, etc.) are created via
frappe.get_doc().insert() — never via direct SQL. This ensures all ERPNext
validation, naming series, and accounting entries are applied correctly.
"""

import frappe


def after_install():
    """Run once when the app is first installed on a site."""
    _create_roles()
    _create_default_workspaces()
    frappe.db.commit()


def after_migrate():
    """Run after every `bench migrate` — must be idempotent."""
    _create_roles()
    frappe.db.commit()


def after_uninstall():
    """Cleanup hook — removes app-specific configuration on uninstall."""
    # Roles are not deleted on uninstall to avoid breaking existing users.
    # Workspaces and custom fields are cleaned up by Frappe automatically
    # when the app is uninstalled via `bench uninstall-app`.
    pass


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

ROLES = [
    {
        "role_name": "Bharat Business Owner",
        "desk_access": 1,
        "home_page": "",
        "restrict_to_domain": "",
    },
    {
        "role_name": "Bharat Business Manager",
        "desk_access": 1,
        "home_page": "",
        "restrict_to_domain": "",
    },
    {
        "role_name": "Bharat Business Cashier",
        "desk_access": 1,
        "home_page": "",
        "restrict_to_domain": "",
    },
    {
        "role_name": "Bharat Business Viewer",
        "desk_access": 0,
        "home_page": "",
        "restrict_to_domain": "",
    },
]


def _create_roles():
    """Create bharat_business roles if they don't already exist."""
    for role_data in ROLES:
        if not frappe.db.exists("Role", role_data["role_name"]):
            role = frappe.get_doc({"doctype": "Role", **role_data})
            role.insert(ignore_permissions=True)
            frappe.logger().info(f"[bharat_business] Created role: {role_data['role_name']}")


def _create_default_workspaces():
    """
    Placeholder — simplified workspaces are created in Milestone 02
    once the DocType fixtures and page assets are ready.
    """
    pass
