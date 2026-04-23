import frappe
from frappe import _


def execute(filters=None):
    filters = filters or {}
    return get_columns(), get_data(filters)


def get_columns():
    return [
        {"label": _("Employee"), "fieldname": "employee", "fieldtype": "Link", "options": "Employee", "width": 140},
        {"label": _("Asset"), "fieldname": "company_asset", "fieldtype": "Link", "options": "Company Asset", "width": 180},
        {"label": _("Category"), "fieldname": "asset_category", "fieldtype": "Link", "options": "Asset Category", "width": 130},
        {"label": _("Expected Return"), "fieldname": "expected_return_date", "fieldtype": "Date", "width": 120},
        {"label": _("Overdue Days"), "fieldname": "overdue_days", "fieldtype": "Int", "width": 110}
    ]


def get_data(filters):
    conditions = [
        "aa.assignment_status = 'Active'",
        "aa.docstatus = 1",
        "aa.expected_return_date < CURDATE()"
    ]
    values = {}

    if filters.get("employee"):
        conditions.append("aa.employee = %(employee)s")
        values["employee"] = filters["employee"]
    if filters.get("asset_category"):
        conditions.append("ca.asset_category = %(asset_category)s")
        values["asset_category"] = filters["asset_category"]

    return frappe.db.sql(
        f"""
        SELECT
            aa.employee,
            aa.company_asset,
            ca.asset_category,
            aa.expected_return_date,
            DATEDIFF(CURDATE(), aa.expected_return_date) AS overdue_days
        FROM `tabAsset Assignment` aa
        INNER JOIN `tabCompany Asset` ca ON ca.name = aa.company_asset
        WHERE {' AND '.join(conditions)}
        ORDER BY overdue_days DESC
        """,
        values,
        as_dict=1,
    )
