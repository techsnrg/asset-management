import frappe
from frappe import _


def execute(filters=None):
    filters = filters or {}
    return get_columns(), get_data(filters)


def get_columns():
    return [
        {"label": _("Assignment"), "fieldname": "assignment_name", "fieldtype": "Link", "options": "Asset Assignment", "width": 140},
        {"label": _("Employee"), "fieldname": "employee", "fieldtype": "Link", "options": "Employee", "width": 140},
        {"label": _("Assigned Date"), "fieldname": "assigned_date", "fieldtype": "Date", "width": 110},
        {"label": _("Expected Return"), "fieldname": "expected_return_date", "fieldtype": "Date", "width": 120},
        {"label": _("Return Date"), "fieldname": "return_date", "fieldtype": "Date", "width": 110},
        {"label": _("Condition At Issue"), "fieldname": "condition_at_issue", "fieldtype": "Data", "width": 130},
        {"label": _("Condition At Return"), "fieldname": "condition_at_return", "fieldtype": "Data", "width": 140},
        {"label": _("Disposition"), "fieldname": "disposition", "fieldtype": "Data", "width": 110},
        {"label": _("Assignment Status"), "fieldname": "assignment_status", "fieldtype": "Data", "width": 130}
    ]


def get_data(filters):
    conditions = ["aa.docstatus = 1"]
    values = {}

    if filters.get("company_asset"):
        conditions.append("aa.company_asset = %(company_asset)s")
        values["company_asset"] = filters["company_asset"]

    return frappe.db.sql(
        f"""
        SELECT
            aa.name AS assignment_name,
            aa.employee,
            aa.assigned_date,
            aa.expected_return_date,
            ar.return_date,
            aa.condition_at_issue,
            ar.condition_at_return,
            ar.disposition,
            aa.assignment_status
        FROM `tabAsset Assignment` aa
        LEFT JOIN `tabAsset Return` ar
            ON ar.asset_assignment = aa.name
            AND ar.docstatus = 1
        WHERE {' AND '.join(conditions)}
        ORDER BY aa.assigned_date DESC
        """,
        values,
        as_dict=1,
    )
