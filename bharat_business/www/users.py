"""
bharat_business/www/users.py

Deprecated legacy route. Redirects Super Administrators to /platform-admin
and completely denies/404s all external and standard users.
"""

import frappe


def get_context(context):
    context.no_cache = 1

    if frappe.session.user == "Administrator":
        frappe.local.flags.redirect_location = "/platform-admin"
        raise frappe.Redirect

    # Completely invisible to any non-administrator
    frappe.local.flags.redirect_location = "/404"
    raise frappe.Redirect
