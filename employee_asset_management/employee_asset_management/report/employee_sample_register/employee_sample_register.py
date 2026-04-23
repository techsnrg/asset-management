import frappe
from frappe import _


def execute(filters=None):
    filters = filters or {}
    return get_columns(), get_data(filters)


def get_columns():
    return [
        {"label": _("Sample Issue"), "fieldname": "name", "fieldtype": "Link", "options": "Employee Sample Issue", "width": 140},
        {"label": _("Employee"), "fieldname": "employee", "fieldtype": "Link", "options": "Employee", "width": 140},
        {"label": _("Delivery Note"), "fieldname": "delivery_note", "fieldtype": "Link", "options": "Delivery Note", "width": 150},
        {"label": _("Issue Date"), "fieldname": "issue_date", "fieldtype": "Date", "width": 110},
        {"label": _("Status"), "fieldname": "status", "fieldtype": "Data", "width": 140},
        {"label": _("Total Qty"), "fieldname": "total_qty", "fieldtype": "Float", "width": 100},
        {"label": _("Outstanding Qty"), "fieldname": "total_outstanding_qty", "fieldtype": "Float", "width": 120},
        {"label": _("Total Issue Value"), "fieldname": "total_issue_value", "fieldtype": "Currency", "width": 130},
        {"label": _("Outstanding Value"), "fieldname": "total_outstanding_value", "fieldtype": "Currency", "width": 140}
    ]


def get_data(filters):
    conditions = ["1=1"]
    values = {}

    if filters.get("employee"):
        conditions.append("employee = %(employee)s")
        values["employee"] = filters["employee"]
    if filters.get("status"):
        conditions.append("status = %(status)s")
        values["status"] = filters["status"]

    return frappe.db.sql(
        f"""
        SELECT
            name,
            employee,
            delivery_note,
            issue_date,
            status,
            total_qty,
            total_outstanding_qty,
            total_issue_value,
            total_outstanding_value
        FROM `tabEmployee Sample Issue`
        WHERE {' AND '.join(conditions)}
        ORDER BY modified DESC
        """,
        values,
        as_dict=1,
    )
