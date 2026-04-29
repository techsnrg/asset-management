import frappe


REQUIRED_ROLES = (
    "Admin",
    "Employee",
    "HR User",
    "HR Manager",
    "IT Manager",
    "Managing Director",
)


def run_setup():
    create_roles()
    seed_settings()
    insert_sample_data()
    frappe.db.commit()


def create_roles():
    for role_name in REQUIRED_ROLES:
        if not frappe.db.exists("Role", role_name):
            frappe.get_doc({"doctype": "Role", "role_name": role_name}).insert(ignore_permissions=True)


def seed_settings():
    settings = frappe.get_single("Asset Management Settings")

    if not settings.default_approver_role:
        settings.default_approver_role = "Managing Director"
    if not settings.reminder_days_before_due:
        settings.reminder_days_before_due = 3
    if not settings.overdue_repeat_days:
        settings.overdue_repeat_days = 2
    if not settings.damage_default_disposition:
        settings.damage_default_disposition = "Maintenance"

    existing_roles = {row.role for row in settings.allowed_on_behalf_requester_roles}
    for role_name in ("HR User", "HR Manager", "Admin", "System Manager"):
        if role_name not in existing_roles:
            settings.append("allowed_on_behalf_requester_roles", {"role": role_name})

    settings.save(ignore_permissions=True)


def insert_sample_data():
    categories = [
        {
            "category_name": "Laptop",
            "max_per_employee": 1,
            "requires_approval": 1,
            "use_default_approver": 1,
            "allowed_issuer_roles": [{"role": "IT Manager"}],
        },
        {
            "category_name": "Mobile Phone",
            "max_per_employee": 1,
            "requires_approval": 1,
            "use_default_approver": 1,
            "allowed_issuer_roles": [{"role": "IT Manager"}],
        },
        {
            "category_name": "Diary",
            "max_per_employee": 1,
            "requires_approval": 1,
            "use_default_approver": 1,
            "allowed_issuer_roles": [{"role": "Admin"}],
        },
        {
            "category_name": "Headset",
            "max_per_employee": 2,
            "requires_approval": 0,
            "auto_approve": 1,
            "use_default_approver": 1,
            "allowed_issuer_roles": [{"role": "IT Manager"}],
        },
    ]

    for category in categories:
        if not frappe.db.exists("Employee Asset Category", category["category_name"]):
            frappe.get_doc({"doctype": "Employee Asset Category", **category}).insert(ignore_permissions=True)

    assets = [
        {
            "asset_name": "MacBook Pro #001",
            "asset_category": "Laptop",
            "serial_number": "SN-MBP-001",
            "brand": "Apple",
            "model": "MacBook Pro 14",
            "vendor": "Apple Store",
            "current_status": "Available",
            "condition": "New",
        },
        {
            "asset_name": "MacBook Pro #002",
            "asset_category": "Laptop",
            "serial_number": "SN-MBP-002",
            "brand": "Apple",
            "model": "MacBook Pro 14",
            "vendor": "Apple Store",
            "current_status": "Available",
            "condition": "New",
        },
        {
            "asset_name": "iPhone 15 #001",
            "asset_category": "Mobile Phone",
            "serial_number": "SN-IP15-001",
            "brand": "Apple",
            "model": "iPhone 15",
            "vendor": "Apple Store",
            "current_status": "Available",
            "condition": "New",
        },
        {
            "asset_name": "Logitech H390 #001",
            "asset_category": "Headset",
            "serial_number": "SN-H390-001",
            "brand": "Logitech",
            "model": "H390",
            "vendor": "Logitech",
            "current_status": "Available",
            "condition": "New",
        },
    ]

    for asset in assets:
        if not frappe.db.exists("Company Asset", asset["asset_name"]):
            frappe.get_doc({"doctype": "Company Asset", **asset}).insert(ignore_permissions=True)
