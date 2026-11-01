"""
bharat_business/hooks.py

All Frappe hook registrations for the bharat_business app.
Hooks are the approved Frappe mechanism for customising ERPNext behaviour
without modifying upstream files.

IMPORTANT: Never bypass ERPNext business logic here. Use hooks to extend,
not to replace.
"""

app_name = "bharat_business"
app_title = "Bharat Business"
app_publisher = "Bharat Business"
app_description = "Indian Small Business Operating Platform built on Frappe + ERPNext"
app_email = "hello@bharatbusiness.in"
app_license = "MIT"
app_icon = "fa fa-store"
app_color = "#FF6B35"  # Saffron — Indian business identity

# Minimum required versions — prevents installation on incompatible stacks
required_apps = ["frappe", "erpnext"]

# ---------------------------------------------------------------------------
# Fixtures — exported configuration that travels with the app
# ---------------------------------------------------------------------------
# All custom fields, property setters, roles and workspaces are managed here.
# Run `bench export-fixtures` to update after changes.
fixtures = [
    # Custom Fields added to ERPNext DocTypes
    {
        "dt": "Custom Field",
        "filters": [["module", "=", "Bharat Business"]],
    },
    # Property Setters (field attribute overrides, e.g. hide ERP terminology)
    {
        "dt": "Property Setter",
        "filters": [["module", "=", "Bharat Business"]],
    },
    # Roles defined by this app
    {
        "dt": "Role",
        "filters": [["role_name", "in", [
            "Bharat Business Owner",
            "Bharat Business Manager",
            "Bharat Business Cashier",
            "Bharat Business Viewer",
        ]]],
    },
    # Workspaces (simplified dashboards per business type)
    {
        "dt": "Workspace",
        "filters": [["module", "=", "Bharat Business"]],
    },
]

# ---------------------------------------------------------------------------
# Install / Migrate hooks
# ---------------------------------------------------------------------------
after_install = "bharat_business.setup.install.after_install"
after_migrate = "bharat_business.setup.install.after_migrate"
after_uninstall = "bharat_business.setup.install.after_uninstall"

# ---------------------------------------------------------------------------
# Document Events
# ---------------------------------------------------------------------------
# These hooks fire on ERPNext DocType events. Do NOT duplicate ERPNext logic —
# only add bharat_business-specific side effects (logging, notifications, etc.)
doc_events = {
    "Sales Invoice": {
        "on_submit": "bharat_business.overrides.sales_invoice.on_submit",
        "on_cancel": "bharat_business.overrides.sales_invoice.on_cancel",
    },
    "Payment Entry": {
        "on_submit": "bharat_business.overrides.payment_entry.on_submit",
    },
    "Customer": {
        "after_insert": "bharat_business.overrides.customer.after_insert",
    },
    "Item": {
        "after_insert": "bharat_business.overrides.item.after_insert",
    },
}

# ---------------------------------------------------------------------------
# Scheduled Tasks
# ---------------------------------------------------------------------------
scheduler_events = {
    "daily": [
        "bharat_business.tasks.daily.run_daily_summary",
    ],
    "weekly": [
        "bharat_business.tasks.weekly.run_weekly_digest",
    ],
}

# ---------------------------------------------------------------------------
# Jinja Template Globals
# ---------------------------------------------------------------------------
# Makes helper functions available in print formats and web templates.
jinja = {
    "methods": [
        "bharat_business.utils.formatting.format_inr",
        "bharat_business.utils.formatting.format_gst_number",
    ]
}

# ---------------------------------------------------------------------------
# Permissions
# ---------------------------------------------------------------------------
# Role-based permission rules for bharat_business DocTypes are defined in
# each DocType's JSON fixture. ERPNext DocType permissions are not modified here.
# Use Permission Manager or DocType fixtures to adjust standard permissions.

# ---------------------------------------------------------------------------
# Website / Portal
# ---------------------------------------------------------------------------
# No public website pages in MVP. Reserved for future customer-portal feature.
website_route_rules = []

# ---------------------------------------------------------------------------
# Boot Session
# ---------------------------------------------------------------------------
# Inject bharat_business context into every boot session.
# Used to load business profile config into the front-end.
boot_session = "bharat_business.setup.boot.boot_session"

# ---------------------------------------------------------------------------
# Override List / Form views (simplified alternatives, not replacements)
# ---------------------------------------------------------------------------
# These override the dashboard links shown in standard ERPNext forms.
# The standard form itself is unchanged — only the embedded dashboard changes.
override_doctype_dashboards = {
    # Stub — populated in Milestone 02 once simplified views are built
}

# ---------------------------------------------------------------------------
# Client Scripts (loaded globally for bharat_business roles)
# ---------------------------------------------------------------------------
app_include_js = [
    "/assets/bharat_business/js/bharat_business.js",
]
app_include_css = [
    "/assets/bharat_business/css/bharat_business.css",
]
