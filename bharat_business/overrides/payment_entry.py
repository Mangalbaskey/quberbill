"""
bharat_business/overrides/payment_entry.py

Side-effect hooks for Payment Entry events.
"""

import frappe


def on_submit(doc, method=None):
    frappe.logger().info(
        f"[bharat_business] Payment received: {doc.name} | "
        f"Party: {doc.party} | Amount: {doc.paid_amount} | "
        f"Mode: {doc.mode_of_payment}"
    )
