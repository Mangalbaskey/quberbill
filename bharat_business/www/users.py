"""
bharat_business/www/users.py

Developer & Admin User Management Dashboard (Supabase Auth Style)
for QuberBill / Bharat Business.
"""

import frappe
from frappe.utils import format_datetime


def get_context(context):
    context.no_cache = 1

    # Only allow logged in Administrator or System Manager
    if frappe.session.user == "Guest":
        frappe.local.flags.redirect_location = "/login?redirect-to=/users"
        raise frappe.Redirect

    roles = frappe.get_roles(frappe.session.user)
    if "System Manager" not in roles and frappe.session.user != "Administrator":
        frappe.throw("Access restricted to Developers and System Administrators.", frappe.PermissionError)

    context.title = "QuberBill Developer Console — User Management"
    context.app_title = "QuberBill"
    context.app_logo = "/assets/bharat_business/images/quberbill-logo.png"
    context.app_icon = "/assets/bharat_business/images/quberbill-icon.png"
    context.favicon = "/assets/bharat_business/images/favicon.png"
    context.current_user = frappe.session.user
    context.csrf_token = frappe.sessions.get_csrf_token()
    return context


def _check_admin_permission():
    if frappe.session.user == "Guest":
        frappe.throw("Authentication required.", frappe.AuthenticationError)
    roles = frappe.get_roles(frappe.session.user)
    if "System Manager" not in roles and frappe.session.user != "Administrator":
        frappe.throw("Permission denied. Only Administrators can manage users.", frappe.PermissionError)


@frappe.whitelist()
def get_users_list():
    """Return all users with roles, status, and metadata."""
    _check_admin_permission()

    users = frappe.get_all(
        "User",
        filters={"name": ["!=", "Guest"]},
        fields=["name", "email", "first_name", "last_name", "full_name", "enabled", "creation", "last_login", "user_image"],
        order_by="creation desc"
    )

    result = []
    for u in users:
        roles = [r for r in frappe.get_roles(u.name) if r not in ("All",)]
        result.append({
            "name": u.name,
            "email": u.email or u.name,
            "first_name": u.first_name or "",
            "last_name": u.last_name or "",
            "full_name": u.full_name or u.first_name or u.name,
            "enabled": bool(u.enabled),
            "creation": format_datetime(u.creation, "yyyy-MM-dd HH:mm") if u.creation else "-",
            "last_login": format_datetime(u.last_login, "yyyy-MM-dd HH:mm") if u.last_login else "Never",
            "roles": roles,
            "is_admin": u.name == "Administrator" or "System Manager" in roles
        })

    return {
        "success": True,
        "users": result,
        "total": len(result),
        "active": sum(1 for u in result if u["enabled"]),
        "disabled": sum(1 for u in result if not u["enabled"])
    }


@frappe.whitelist()
def create_user(email, first_name, last_name=None, password=None, role="Bharat Business Owner"):
    """Create a new user, assign role, and set initial password."""
    _check_admin_permission()

    email = (email or "").strip().lower()
    if not email:
        frappe.throw("Email is required.")

    if frappe.db.exists("User", email):
        frappe.throw(f"User with email '{email}' already exists.")

    user = frappe.get_doc({
        "doctype": "User",
        "email": email,
        "first_name": (first_name or "").strip() or email.split("@")[0],
        "last_name": (last_name or "").strip(),
        "enabled": 1,
        "send_welcome_email": 0,
        "user_type": "System User"
    })
    user.insert(ignore_permissions=True)

    # Assign default and custom roles
    standard_roles = ["Bharat Business Owner", "Stock User", "Sales User", "Accounts User"]
    target_role = (role or "Bharat Business Owner").strip()
    user.add_roles(target_role)

    # Also assign subordinate roles for POS/billing access
    for r in ["Stock User", "Sales User", "Accounts User"]:
        if r != target_role and frappe.db.exists("Role", r):
            user.add_roles(r)

    # Set password if provided
    if password and password.strip():
        from frappe.utils.password import update_password
        update_password(user=email, pwd=password.strip())

    frappe.db.commit()
    return {"success": True, "message": f"User {email} created successfully."}


@frappe.whitelist()
def update_user_password(user, new_password):
    """Set or change a user's password directly."""
    _check_admin_permission()

    user = (user or "").strip()
    new_password = (new_password or "").strip()

    if not frappe.db.exists("User", user):
        frappe.throw(f"User {user} does not exist.")

    if len(new_password) < 4:
        frappe.throw("Password must be at least 4 characters long.")

    from frappe.utils.password import update_password
    update_password(user=user, pwd=new_password)
    frappe.db.commit()

    return {"success": True, "message": f"Password updated for {user}."}


@frappe.whitelist()
def toggle_user_status(user, enabled):
    """Enable or disable a user account."""
    _check_admin_permission()

    user = (user or "").strip()
    if user == "Administrator":
        frappe.throw("The Administrator account cannot be disabled.")

    if not frappe.db.exists("User", user):
        frappe.throw(f"User {user} does not exist.")

    status_val = 1 if int(enabled) else 0
    frappe.db.set_value("User", user, "enabled", status_val)
    frappe.db.commit()

    status_label = "enabled" if status_val else "disabled"
    return {"success": True, "message": f"User {user} has been {status_label}."}


@frappe.whitelist()
def delete_user(user):
    """Permanently delete a user."""
    _check_admin_permission()

    user = (user or "").strip()
    if user in ("Administrator", "Guest"):
        frappe.throw(f"Cannot delete system user '{user}'.")

    if not frappe.db.exists("User", user):
        frappe.throw(f"User {user} does not exist.")

    frappe.delete_doc("User", user, ignore_permissions=True)
    frappe.db.commit()

    return {"success": True, "message": f"User {user} has been deleted."}
