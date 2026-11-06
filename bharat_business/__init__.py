"""
bharat_business

QuberBill — Smart Billing & Operating Platform for Indian Businesses.
"""

__version__ = "1.0.0"

# ---------------------------------------------------------------------------
# Monkey-patch Frappe & ERPNext v16 Setup Wizard bug where country/currency is None
# ---------------------------------------------------------------------------
def _patch_setup_wizard():
    try:
        import frappe.desk.page.setup_wizard.setup_wizard as frappe_sw
        import json

        _orig_sw_setup_complete = frappe_sw.setup_complete

        def _patched_sw_setup_complete(args=None):
            parsed = {}
            if isinstance(args, str):
                try:
                    parsed = json.loads(args)
                except Exception:
                    parsed = {}
            elif isinstance(args, dict):
                parsed = dict(args)

            # Ensure all regional defaults for India
            if not parsed.get("country"):
                parsed["country"] = "India"
            if not parsed.get("currency"):
                parsed["currency"] = "INR"
            if not parsed.get("timezone"):
                parsed["timezone"] = "Asia/Kolkata"
            if not parsed.get("language"):
                parsed["language"] = "en"

            # Serialize back if it was string
            if isinstance(args, str):
                args = json.dumps(parsed)
            else:
                args = parsed

            return _orig_sw_setup_complete(args)

        frappe_sw.setup_complete = _patched_sw_setup_complete

    except Exception:
        pass

    try:
        import erpnext.setup.setup_wizard.operations.install_fixtures as fixtures

        _orig_install = fixtures.install
        def _patched_install(country=None):
            if not country:
                country = "India"
            return _orig_install(country)
        fixtures.install = _patched_install

        _orig_install_defaults = fixtures.install_defaults
        def _patched_install_defaults(args=None):
            if args is not None:
                if not args.get("currency"):
                    args["currency"] = "INR"
                if not args.get("country"):
                    args["country"] = "India"
            return _orig_install_defaults(args)
        fixtures.install_defaults = _patched_install_defaults

        import erpnext.setup.setup_wizard.setup_wizard as erp_setup

        _orig_stage_fixtures = erp_setup.stage_fixtures
        def _patched_stage_fixtures(args):
            if isinstance(args, dict):
                if not args.get("country"):
                    args["country"] = "India"
                if not args.get("currency"):
                    args["currency"] = "INR"
            return _orig_stage_fixtures(args)
        erp_setup.stage_fixtures = _patched_stage_fixtures

        _orig_setup_company = erp_setup.setup_company
        def _patched_setup_company(args):
            if isinstance(args, dict):
                if not args.get("country"):
                    args["country"] = "India"
                if not args.get("currency"):
                    args["currency"] = "INR"
            return _orig_setup_company(args)
        erp_setup.setup_company = _patched_setup_company

        _orig_setup_defaults = erp_setup.setup_defaults
        def _patched_setup_defaults(args):
            if isinstance(args, dict):
                if not args.get("currency"):
                    args["currency"] = "INR"
                if not args.get("country"):
                    args["country"] = "India"
            return _orig_setup_defaults(args)
        erp_setup.setup_defaults = _patched_setup_defaults

    except Exception:
        pass


_patch_setup_wizard()
