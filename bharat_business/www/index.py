"""
bharat_business/www/index.py

Landing page context for QuberBill.
"""

import frappe


def get_context(context):
    context.no_cache = 1
    context.title = "QuberBill — Smart Billing & Operating Platform for Indian Businesses"
    context.app_title = "QuberBill"
    context.app_logo = "/assets/bharat_business/images/quberbill-logo.png"
    context.app_icon = "/assets/bharat_business/images/quberbill-icon.png"
    context.favicon = "/assets/bharat_business/images/favicon.png"
    return context
