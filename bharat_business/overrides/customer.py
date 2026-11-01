"""bharat_business/overrides/customer.py"""

import frappe


def after_insert(doc, method=None):
    frappe.logger().info(
        f"[bharat_business] New customer: {doc.name} | Company: {doc.default_company}"
    )
