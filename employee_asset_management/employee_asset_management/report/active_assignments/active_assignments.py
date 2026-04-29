import frappe
from frappe import _


def execute(filters=None):
    filters = filters or {}
    return get_columns(), get_data(filters)


def get_columns():
    return [
        {"label": _("Employee"), "fieldname": "employee", "fieldtype": "Link", "options": "Employee", "width": 140},
        {"label": _("Asset"), "fieldname": "company_asset", "fieldtype": "Link", "options": "Company Asset", "width": 180},
        {"label": _("Employee Asset Category"), "fieldname": "asset_category", "fieldtype": "Link", "options": "Employee Asset Category", "width": 160},
        {"label": _("Assigned By"), "fieldname": "assigned_by", "fieldtype": "Link", "options": "User", "width": 130},
        {"label": _("Assigned Date"), "fieldname": "assigned_date", "fieldtype": "Date", "width": 110},
        {"label": _("Expected Return"), "fieldname": "expected_return_date", "fieldtype": "Date", "width": 120}
    ]


def get_data(filters):
    conditions = ["aa.assignment_status = 'Active'", "aa.docstatus = 1"]
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
            aa.assigned_by,
            aa.assigned_date,
            aa.expected_return_date
        FROM `tabAsset Assignment` aa
        INNER JOIN `tabCompany Asset` ca ON ca.name = aa.company_asset
        WHERE {' AND '.join(conditions)}
        ORDER BY aa.expected_return_date ASC, aa.modified DESC
        """,
        values,
        as_dict=1,
    )
