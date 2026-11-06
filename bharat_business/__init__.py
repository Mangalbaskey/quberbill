"""
bharat_business

QuberBill — Smart Billing & Operating Platform for Indian Businesses.
"""

__version__ = "1.0.0"

# ---------------------------------------------------------------------------
# Monkey-patch ERPNext v16 Setup Wizard bug where country is None
# ---------------------------------------------------------------------------
def _patch_erpnext_setup_wizard():
    try:
        import erpnext.setup.setup_wizard.operations.install_fixtures as fixtures

        _orig_install = fixtures.install
        def _patched_install(country=None):
            if not country:
                country = "India"
            return _orig_install(country)
        fixtures.install = _patched_install

        import erpnext.setup.setup_wizard.setup_wizard as erp_setup

        _orig_stage_fixtures = erp_setup.stage_fixtures
        def _patched_stage_fixtures(args):
            if isinstance(args, dict) and not args.get("country"):
                args["country"] = "India"
            return _orig_stage_fixtures(args)
        erp_setup.stage_fixtures = _patched_stage_fixtures

        _orig_setup_company = erp_setup.setup_company
        def _patched_setup_company(args):
            if isinstance(args, dict) and not args.get("country"):
                args["country"] = "India"
            return _orig_setup_company(args)
        erp_setup.setup_company = _patched_setup_company

    except Exception:
        pass

_patch_erpnext_setup_wizard()
