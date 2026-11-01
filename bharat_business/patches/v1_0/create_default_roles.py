"""
bharat_business/patches/v1_0/create_default_roles.py

Migration patch: ensure bharat_business roles exist.
This patch is idempotent — safe to run multiple times.
"""

import frappe
from bharat_business.setup.install import _create_roles


def execute():
    _create_roles()
    frappe.db.commit()
