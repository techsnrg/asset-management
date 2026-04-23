import frappe
from frappe import _


def execute(filters=None):
    filters = filters or {}
    return get_columns(), get_data(filters)


def get_columns():
    return [
        {"label": _("Employee"), "fieldname": "employee_name", "fieldtype": "Data", "width": 160},
        {"label": _("Requested By"), "fieldname": "requested_by", "fieldtype": "Link", "options": "User", "width": 140},
        {"label": _("Asset Category"), "fieldname": "asset_category", "fieldtype": "Link", "options": "Asset Category", "width": 130},
        {"label": _("Asset Name"), "fieldname": "asset_name", "fieldtype": "Link", "options": "Company Asset", "width": 180},
        {"label": _("Serial Number"), "fieldname": "serial_number", "fieldtype": "Data", "width": 130},
        {"label": _("Assigned Date"), "fieldname": "assigned_date", "fieldtype": "Date", "width": 110},
        {"label": _("Expected Return"), "fieldname": "expected_return_date", "fieldtype": "Date", "width": 120},
        {"label": _("Assignment Status"), "fieldname": "assignment_status", "fieldtype": "Data", "width": 130},
        {"label": _("Current Asset Status"), "fieldname": "current_status", "fieldtype": "Data", "width": 140},
    ]


def get_data(filters):
    conditions = []
    values = {}

    if filters.get("employee"):
        conditions.append("aa.employee = %(employee)s")
        values["employee"] = filters["employee"]
    if filters.get("asset_category"):
        conditions.append("ca.asset_category = %(asset_category)s")
        values["asset_category"] = filters["asset_category"]
    if filters.get("assignment_status"):
        conditions.append("aa.assignment_status = %(assignment_status)s")
        values["assignment_status"] = filters["assignment_status"]

    where_clause = " AND ".join(conditions)
    if where_clause:
        where_clause = " AND " + where_clause

    return frappe.db.sql(
        f"""
        SELECT
            e.employee_name,
            ar.requested_by,
            ca.asset_category,
            ca.asset_name,
            ca.serial_number,
            aa.assigned_date,
            aa.expected_return_date,
            aa.assignment_status,
            ca.current_status
        FROM `tabAsset Assignment` aa
        INNER JOIN `tabEmployee` e ON e.name = aa.employee
        INNER JOIN `tabCompany Asset` ca ON ca.name = aa.company_asset
        LEFT JOIN `tabAsset Request` ar ON ar.name = aa.asset_request
        WHERE aa.docstatus = 1 {where_clause}
        ORDER BY aa.assigned_date DESC
        """,
        values,
        as_dict=1,
    )
