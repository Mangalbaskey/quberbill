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
    _setup_branding()
    frappe.db.commit()


def after_migrate():
    """Run after every `bench migrate` — must be idempotent."""
    _create_roles()
    _setup_branding()
    frappe.db.commit()


def after_uninstall():
    """Cleanup hook — removes app-specific configuration on uninstall."""
    # Roles are not deleted on uninstall to avoid breaking existing users.
    # Workspaces and custom fields are cleaned up by Frappe automatically
    # when the app is uninstalled via `bench uninstall-app`.
    pass


def _setup_branding():
    """Apply QuberBill branding to Website Settings, Navbar Settings, and System Settings."""
    try:
        # Website Settings
        if frappe.db.exists("DocType", "Website Settings"):
            ws = frappe.get_single("Website Settings")
            ws.app_name = "QuberBill"
            ws.home_page = "index"
            ws.app_logo = "/assets/bharat_business/images/quberbill-logo.png"
            ws.favicon = "/assets/bharat_business/images/favicon.png"
            ws.splash_image = "/assets/bharat_business/images/quberbill-logo.png"
            ws.banner_image = "/assets/bharat_business/images/quberbill-logo.png"
            ws.brand_html = '<img src="/assets/bharat_business/images/quberbill-logo.png" style="max-height: 32px;" alt="QuberBill">'
            ws.disable_signup = 0  # Enable public user registration on /login
            ws.hide_footer_signup = 0
            ws.save(ignore_permissions=True)
            frappe.db.commit()

        # Navbar Settings
        if frappe.db.exists("DocType", "Navbar Settings"):
            ns = frappe.get_single("Navbar Settings")
            ns.app_logo = "/assets/bharat_business/images/quberbill-logo.png"
            ns.save(ignore_permissions=True)

        # System Settings
        if frappe.db.exists("DocType", "System Settings"):
            ss = frappe.get_single("System Settings")
            ss.app_name = "QuberBill"
            if not ss.country:
                ss.country = "India"
            if not ss.currency:
                ss.currency = "INR"
            if not ss.time_zone:
                ss.time_zone = "Asia/Kolkata"
            ss.save(ignore_permissions=True)

        # Global Defaults
        if frappe.db.exists("DocType", "Global Defaults"):
            gd = frappe.get_single("Global Defaults")
            if not gd.default_currency:
                gd.default_currency = "INR"
            if not gd.country:
                gd.country = "India"
            gd.save(ignore_permissions=True)

        frappe.logger().info("[bharat_business] Applied QuberBill branding successfully")
    except Exception:
        frappe.log_error(frappe.get_traceback(), "[bharat_business] branding setup error")


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


def after_user_signup(doc, method=None):
    """Automatically grant desk access and roles to newly registered QuberBill users."""
    if not doc or doc.name in ("Administrator", "Guest"):
        return
    try:
        # Give System User access so they can log into Desk / POS
        if doc.user_type != "System User":
            frappe.db.set_value("User", doc.name, "user_type", "System User")

        # Grant business owner & billing roles
        for r in ["Bharat Business Owner", "Stock User", "Sales User", "Accounts User"]:
            if frappe.db.exists("Role", r):
                doc.add_roles(r)
        frappe.db.commit()
    except Exception:
        frappe.log_error(frappe.get_traceback(), "[bharat_business] after_user_signup error")
