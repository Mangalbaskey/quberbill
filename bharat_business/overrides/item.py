"""bharat_business/overrides/item.py"""

import frappe


def after_insert(doc, method=None):
    frappe.logger().info(f"[bharat_business] New item: {doc.name} | Group: {doc.item_group}")
