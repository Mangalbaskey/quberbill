"""
bharat_business/www/platform_admin.py

Dedicated Super Administrator & SaaS Control Plane for QuberBill.
Strictly isolated from customer / tenant workspaces.

Only accessible by the Platform Super Administrator (frappe.session.user == "Administrator").
All other users and guests are redirected to 404 to protect platform privacy.
"""

import frappe
from frappe.utils import format_datetime


def get_context(context):
    context.no_cache = 1

    # Security boundary: Only platform super administrator can access
    if frappe.session.user == "Guest":
        frappe.local.flags.redirect_location = "/login"
        raise frappe.Redirect

    if frappe.session.user != "Administrator":
        # Return 404 so regular users/clients cannot confirm this portal exists
        frappe.local.flags.redirect_location = "/404"
        raise frappe.Redirect

    context.title = "QuberBill Platform Administration — SaaS Control Plane"
    context.app_title = "QuberBill"
    context.app_logo = "/assets/bharat_business/images/quberbill-logo.png"
    context.app_icon = "/assets/bharat_business/images/quberbill-icon.png"
    context.favicon = "/assets/bharat_business/images/favicon.png"
    context.current_user = frappe.session.user
    context.csrf_token = frappe.sessions.get_csrf_token()
    return context


def _ensure_super_admin():
    """Ensure the caller is strictly the Platform Super Administrator."""
    if frappe.session.user != "Administrator":
        frappe.throw(
            "Access denied. Platform Administration is restricted strictly to Super Administrator.",
            frappe.PermissionError
        )


@frappe.whitelist()
def get_platform_overview():
    """Return top-level SaaS metrics for businesses and accounts."""
    _ensure_super_admin()

    total_businesses = frappe.db.count("BB Business Profile")
    active_businesses = frappe.db.count("BB Business Profile", {"is_active": 1})
    onboarded_businesses = frappe.db.count("BB Business Profile", {"onboarding_complete": 1})

    total_users = frappe.db.count("User", {"name": ["not in", ["Guest", "Administrator"]]})
    active_users = frappe.db.count("User", {"name": ["not in", ["Guest", "Administrator"]], "enabled": 1})

    return {
        "success": True,
        "metrics": {
            "total_businesses": total_businesses,
            "active_businesses": active_businesses,
            "onboarded_businesses": onboarded_businesses,
            "total_users": total_users,
            "active_users": active_users,
        }
    }


@frappe.whitelist()
def get_businesses():
    """
    Return all registered client businesses with their owner,
    GSTIN, status, and creation date.
    """
    _ensure_super_admin()

    profiles = frappe.get_all(
        "BB Business Profile",
        fields=[
            "name",
            "profile_name",
            "company",
            "business_type",
            "is_active",
            "onboarding_complete",
            "gst_category",
            "gstin",
            "place_of_supply_state",
            "annual_turnover_cr",
            "created_by",
            "creation"
        ],
        order_by="creation desc"
    )

    businesses = []
    for p in profiles:
        owner_name = frappe.db.get_value("User", p.created_by, "full_name") or p.created_by
        businesses.append({
            "name": p.name,
            "profile_name": p.profile_name or p.name,
            "company": p.company or "-",
            "business_type": (p.business_type or "retail").capitalize(),
            "gst_category": p.gst_category or "Unregistered",
            "gstin": p.gstin or "-",
            "state": p.place_of_supply_state or "-",
            "annual_turnover_cr": p.annual_turnover_cr or 0,
            "is_active": bool(p.is_active),
            "onboarding_complete": bool(p.onboarding_complete),
            "owner_email": p.created_by or "-",
            "owner_name": owner_name,
            "creation": format_datetime(p.creation, "yyyy-MM-dd HH:mm") if p.creation else "-"
        })

    return {
        "success": True,
        "businesses": businesses,
        "total": len(businesses),
        "active": sum(1 for b in businesses if b["is_active"])
    }


@frappe.whitelist()
def get_accounts():
    """
    Return all user accounts on the platform with assigned roles,
    linked business/company, and activity status.
    """
    _ensure_super_admin()

    users = frappe.get_all(
        "User",
        filters={"name": ["!=", "Guest"]},
        fields=[
            "name", "email", "first_name", "last_name", "full_name",
            "enabled", "creation", "last_login", "user_image"
        ],
        order_by="creation desc"
    )

    result = []
    for u in users:
        roles = [r for r in frappe.get_roles(u.name) if r not in ("All",)]
        
        # Determine associated company from User Permission
        company = frappe.db.get_value("User Permission", {"user": u.name, "allow": "Company"}, "for_value")
        if not company:
            # Fallback to BB Business Profile created_by
            company = frappe.db.get_value("BB Business Profile", {"created_by": u.name}, "company")

        result.append({
            "name": u.name,
            "email": u.email or u.name,
            "full_name": u.full_name or u.first_name or u.name,
            "enabled": bool(u.enabled),
            "company": company or "Global / Unassigned",
            "creation": format_datetime(u.creation, "yyyy-MM-dd HH:mm") if u.creation else "-",
            "last_login": format_datetime(u.last_login, "yyyy-MM-dd HH:mm") if u.last_login else "Never",
            "roles": roles,
            "is_admin": u.name == "Administrator" or "System Manager" in roles
        })

    return {
        "success": True,
        "accounts": result,
        "total": len(result),
        "active": sum(1 for u in result if u["enabled"]),
        "disabled": sum(1 for u in result if not u["enabled"])
    }


@frappe.whitelist()
def toggle_business_status(business_name, is_active):
    """Enable or pause a client business profile."""
    _ensure_super_admin()

    business_name = (business_name or "").strip()
    if not frappe.db.exists("BB Business Profile", business_name):
        frappe.throw(f"Business profile '{business_name}' does not exist.")

    active_val = 1 if int(is_active) else 0
    frappe.db.set_value("BB Business Profile", business_name, "is_active", active_val)
    frappe.db.commit()

    label = "activated" if active_val else "paused"
    return {"success": True, "message": f"Business '{business_name}' has been {label}."}


@frappe.whitelist()
def toggle_account_status(user, enabled):
    """Enable or disable a user account."""
    _ensure_super_admin()

    user = (user or "").strip()
    if user == "Administrator":
        frappe.throw("The Administrator account cannot be disabled.")

    if not frappe.db.exists("User", user):
        frappe.throw(f"User '{user}' does not exist.")

    status_val = 1 if int(enabled) else 0
    frappe.db.set_value("User", user, "enabled", status_val)
    frappe.db.commit()

    label = "enabled" if status_val else "disabled"
    return {"success": True, "message": f"Account '{user}' has been {label}."}


@frappe.whitelist()
def reset_account_password(user, new_password):
    """Reset the password for a user account."""
    _ensure_super_admin()

    user = (user or "").strip()
    if not user or not new_password:
        frappe.throw("User and new password are required.")

    if not frappe.db.exists("User", user):
        frappe.throw(f"User '{user}' does not exist.")

    from frappe.utils.password import update_password
    update_password(user=user, pwd=new_password)
    frappe.db.commit()

    return {"success": True, "message": f"Password for {user} updated successfully."}


@frappe.whitelist()
def create_tenant_user(email, first_name, last_name=None, password=None, role="Bharat Business Owner"):
    """Create a new client business account directly from platform admin."""
    _ensure_super_admin()

    email = (email or "").strip().lower()
    if not email:
        frappe.throw("Email is required.")

    if frappe.db.exists("User", email):
        frappe.throw(f"User '{email}' already exists.")

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

    if role and frappe.db.exists("Role", role):
        user.add_roles(role)

    # Standard operational roles for business clients
    for r in ["Stock User", "Sales User", "Accounts User"]:
        if frappe.db.exists("Role", r):
            user.add_roles(r)

    if password:
        from frappe.utils.password import update_password
        update_password(user=email, pwd=password)

    frappe.db.commit()
    return {"success": True, "message": f"Account {email} created successfully."}
