"""
bharat_business/overrides/sales_invoice.py

Side-effect hooks for Sales Invoice events.
Do NOT implement accounting logic here — ERPNext handles that internally.
Only bharat_business-specific actions (notifications, logging, stats) go here.
"""

import frappe


def on_submit(doc, method=None):
    """
    Fired after ERPNext has fully submitted the Sales Invoice,
    including all GL entries and stock movements.
    """
    _log_sale_event(doc)


def on_cancel(doc, method=None):
    """
    Fired after ERPNext has cancelled the Sales Invoice and
    reversed all GL entries.
    """
    frappe.logger().info(
        f"[bharat_business] Sales Invoice cancelled: {doc.name} | "
        f"Company: {doc.company} | Amount: {doc.grand_total}"
    )


def _log_sale_event(doc):
    """Log key sale data for daily summary computation."""
    frappe.logger().info(
        f"[bharat_business] Sales Invoice submitted: {doc.name} | "
        f"Company: {doc.company} | Customer: {doc.customer} | "
        f"Amount: {doc.grand_total} | GST: {doc.total_taxes_and_charges}"
    )
