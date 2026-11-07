"""
bharat_business/setup/onboarding_service.py

The OnboardingService is the single Python class responsible for translating
wizard answers into ERPNext documents.

It is deliberately separate from the DocType controller so it can be:
  - Unit tested without a running Frappe site
  - Called from the Frappe Page API endpoint
  - Reused in future CLI / bulk-import workflows

RULE: Every ERPNext document created here must go through frappe.get_doc().insert()
      or frappe.get_doc().save() — never frappe.db.sql() INSERT.
"""

import json

import frappe
from frappe import _
from frappe.utils import now_datetime


class OnboardingService:
    """
    Orchestrates the multi-step onboarding wizard.

    Usage:
        service = OnboardingService(wizard_name="WIZ-My Company-0001")
        service.provision_all(wizard_data)
    """

    def __init__(self, wizard_name: str):
        self.wizard = frappe.get_doc("BB Onboarding Wizard", wizard_name)
        self._step_data = json.loads(self.wizard.step_data or "{}")

    # ------------------------------------------------------------------
    # Public entry point
    # ------------------------------------------------------------------

    def provision_all(self):
        """
        Execute all provisioning steps in sequence.
        Called after the last wizard step is saved.
        Returns a dict with provisioning results.
        """
        results = {}

        with frappe.db.savepoint("bb_onboarding"):
            results["company"] = self._provision_company()
            results["profile"] = self._provision_business_profile()
            results["chart_of_accounts"] = self._setup_india_coa()
            results["gst_settings"] = self._setup_gst()
            results["warehouses"] = self._provision_warehouses()
            results["roles"] = self._assign_owner_role()

        self.wizard.complete_wizard()
        return results

    # ------------------------------------------------------------------
    # Step provisioners (called in sequence — order matters)
    # ------------------------------------------------------------------

    def _provision_company(self) -> str:
        """
        Create the ERPNext Company document.
        Returns the company name.
        """
        step1 = self._step_data.get("step_1", {})
        step2 = self._step_data.get("step_2", {})
        step4 = self._step_data.get("step_4", {})
        step6 = self._step_data.get("step_6", {})

        company_name = step2.get("business_name", "").strip()
        if not company_name:
            frappe.throw(_("Business name is required."))

        if frappe.db.exists("Company", company_name):
            # Company already exists (wizard resumed after interruption)
            return company_name

        company = frappe.get_doc(
            {
                "doctype": "Company",
                "company_name": company_name,
                "abbr": self._make_abbr(company_name),
                "default_currency": "INR",
                "country": "India",
                "domain": self._map_domain(step1.get("business_type")),
                # Fiscal year April–March (standard Indian fiscal year)
                "fy_start_date": f"{frappe.utils.getdate().year}-04-01",
                "fy_end_date": f"{frappe.utils.getdate().year + 1}-03-31",
                "gstin": step4.get("gstin", ""),
                "default_letter_head": "",
            }
        )
        company.flags.ignore_mandatory = False
        company.insert(ignore_permissions=True)
        frappe.logger().info(f"[bharat_business] Company created: {company_name}")
        return company_name

    def _provision_business_profile(self) -> str:
        """Create BB Business Profile linked to the Company."""
        step1 = self._step_data.get("step_1", {})
        step2 = self._step_data.get("step_2", {})
        step4 = self._step_data.get("step_4", {})
        step7 = self._step_data.get("step_7", {})

        company_name = step2.get("business_name", "").strip()
        profile_name = f"{company_name} Profile"

        if frappe.db.exists("BB Business Profile", profile_name):
            return profile_name

        profile = frappe.get_doc(
            {
                "doctype": "BB Business Profile",
                "profile_name": profile_name,
                "company": company_name,
                "business_type": step1.get("business_type"),
                "gst_category": step4.get("gst_category", "Unregistered"),
                "gstin": step4.get("gstin", ""),
                "enable_inventory": int(step7.get("enable_inventory", 1)),
                "is_active": 1,
            }
        )
        profile.insert(ignore_permissions=True)

        # Link wizard to profile
        self.wizard.business_profile = profile_name
        self.wizard.save(ignore_permissions=True)

        return profile_name

    def _setup_india_coa(self) -> bool:
        """
        Trigger ERPNext's India Chart of Accounts setup.
        ERPNext automatically selects the India localization CoA when
        country = 'India' during Company creation.
        This step verifies it was applied.
        """
        step2 = self._step_data.get("step_2", {})
        company_name = step2.get("business_name", "").strip()

        root_accounts = frappe.db.count(
            "Account", {"company": company_name, "is_group": 1, "parent_account": ""}
        )
        if root_accounts < 4:
            frappe.log_error(
                f"[bharat_business] CoA appears incomplete for {company_name}: "
                f"only {root_accounts} root accounts found."
            )
            return False
        return True

    def _setup_gst(self) -> bool:
        """
        Configure GST settings via India Compliance app.
        Only runs if india_compliance is installed.
        """
        if not frappe.db.exists("DocType", "GST Settings"):
            # india_compliance not installed — skip silently
            frappe.logger().warning(
                "[bharat_business] india_compliance not installed — GST setup skipped."
            )
            return False

        step4 = self._step_data.get("step_4", {})
        step2 = self._step_data.get("step_2", {})
        company_name = step2.get("business_name", "").strip()
        gst_category = step4.get("gst_category", "Unregistered")

        gst_settings = frappe.get_doc("GST Settings")
        # Add company to GST Settings if not already present
        company_already_added = any(
            row.company == company_name for row in (gst_settings.get("gst_accounts") or [])
        )
        if not company_already_added:
            # india_compliance manages the actual GST account mapping;
            # we only set the top-level toggles here.
            if gst_category != "Unregistered":
                gst_settings.enable_api = 1
            gst_settings.save(ignore_permissions=True)

        return True

    def _provision_warehouses(self) -> list:
        """
        Create one ERPNext Warehouse per branch if inventory is enabled.
        Returns list of created warehouse names.
        """
        step2 = self._step_data.get("step_2", {})
        step7 = self._step_data.get("step_7", {})
        step8 = self._step_data.get("step_8", {})

        if not int(step7.get("enable_inventory", 1)):
            return []

        company_name = step2.get("business_name", "").strip()
        num_branches = int(step8.get("number_of_branches", 1))
        created = []

        for i in range(1, num_branches + 1):
            wh_name = f"{'Main' if i == 1 else f'Branch {i}'} - {company_name[:4].upper()}"
            if not frappe.db.exists("Warehouse", {"warehouse_name": wh_name, "company": company_name}):
                wh = frappe.get_doc(
                    {
                        "doctype": "Warehouse",
                        "warehouse_name": wh_name,
                        "company": company_name,
                        "warehouse_type": "Stores",
                    }
                )
                wh.insert(ignore_permissions=True)
                created.append(wh.name)

        return created

    def _assign_owner_role(self) -> bool:
        """
        Assign 'Bharat Business Owner' role and strict Company User Permission
        to the user who registered, ensuring complete tenant isolation.
        """
        user = frappe.session.user
        if user == "Administrator":
            return True

        user_doc = frappe.get_doc("User", user)
        existing_roles = [r.role for r in user_doc.roles]
        if "Bharat Business Owner" not in existing_roles:
            user_doc.append("roles", {"role": "Bharat Business Owner"})
            user_doc.save(ignore_permissions=True)

        # Multi-tenancy: restrict this user strictly to their own business/company
        step2 = self._step_data.get("step_2", {})
        company_name = step2.get("business_name", "").strip()
        if company_name and not frappe.db.exists(
            "User Permission",
            {"user": user, "allow": "Company", "for_value": company_name}
        ):
            perm = frappe.get_doc({
                "doctype": "User Permission",
                "user": user,
                "allow": "Company",
                "for_value": company_name,
                "is_default": 1,
            })
            perm.insert(ignore_permissions=True)
            frappe.defaults.set_user_default("company", company_name, user)

        return True

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _make_abbr(company_name: str) -> str:
        """Generate a short abbreviation from the company name."""
        words = company_name.split()
        abbr = "".join(w[0].upper() for w in words[:3])
        return abbr or company_name[:3].upper()

    @staticmethod
    def _map_domain(business_type: str) -> str:
        """Map bharat_business type to ERPNext domain."""
        domain_map = {
            "retail": "Retail",
            "grocery": "Retail",
            "wholesale": "Distribution",
            "restaurant": "Food and Beverage",
            "service_repair": "Services",
            "freelancer_agency": "Services",
            "manufacturing": "Manufacturing",
        }
        return domain_map.get(business_type, "Retail")


# ---------------------------------------------------------------------------
# Frappe whitelisted API — called from the onboarding wizard Frappe Page
# ---------------------------------------------------------------------------

@frappe.whitelist()
def provision_from_wizard(wizard_name: str):
    """
    Entry point called by the front-end once all wizard steps are saved.
    Must be called as the authenticated business owner, not Administrator.
    """
    frappe.only_for(["Bharat Business Owner", "System Manager", "Administrator"])
    service = OnboardingService(wizard_name)
    return service.provision_all()
