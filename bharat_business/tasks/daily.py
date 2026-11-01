"""bharat_business/tasks/daily.py — Daily scheduled tasks."""

import frappe


def run_daily_summary():
    """
    Placeholder for daily sales summary computation.
    Full implementation in Milestone 03 (Dashboard).
    """
    frappe.logger().info("[bharat_business] Daily summary task ran.")
