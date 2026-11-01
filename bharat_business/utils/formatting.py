"""
bharat_business/utils/formatting.py

Formatting utilities for Indian currency and GST numbers.
These functions are also registered as Jinja globals in hooks.py
so they can be used in print formats and email templates.
"""

import re


def format_inr(amount, show_symbol: bool = True) -> str:
    """
    Format a number using Indian numbering system (lakhs / crores).

    Examples:
        format_inr(1234567.50)  ->  '₹12,34,567.50'
        format_inr(1234567.50, show_symbol=False)  ->  '12,34,567.50'
    """
    if amount is None:
        return ""

    try:
        amount = float(amount)
    except (TypeError, ValueError):
        return str(amount)

    # Format with 2 decimal places
    integer_part, decimal_part = f"{abs(amount):.2f}".split(".")

    # Indian grouping: last 3 digits, then groups of 2
    if len(integer_part) > 3:
        last_three = integer_part[-3:]
        rest = integer_part[:-3]
        # Group rest in pairs from the right
        pairs = []
        while len(rest) > 2:
            pairs.append(rest[-2:])
            rest = rest[:-2]
        if rest:
            pairs.append(rest)
        pairs.reverse()
        formatted_int = ",".join(pairs) + "," + last_three
    else:
        formatted_int = integer_part

    sign = "-" if amount < 0 else ""
    symbol = "₹" if show_symbol else ""
    return f"{sign}{symbol}{formatted_int}.{decimal_part}"


def format_gst_number(gstin: str) -> str:
    """
    Format GSTIN for display: add spaces for readability.
    22AAAAA0000A1Z5  ->  22 AAAAA0000A 1 Z 5
    """
    if not gstin or len(gstin) != 15:
        return gstin or ""
    gstin = gstin.upper()
    return f"{gstin[:2]} {gstin[2:12]} {gstin[12]} {gstin[13]} {gstin[14]}"


def format_phone_india(phone: str) -> str:
    """
    Normalise Indian phone numbers to +91-XXXXX-XXXXX format.
    """
    if not phone:
        return ""
    digits = re.sub(r"\D", "", phone)
    if digits.startswith("91") and len(digits) == 12:
        digits = digits[2:]
    if len(digits) == 10:
        return f"+91-{digits[:5]}-{digits[5:]}"
    return phone
