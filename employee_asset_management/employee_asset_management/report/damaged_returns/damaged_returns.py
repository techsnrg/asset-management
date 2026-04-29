import frappe
from frappe import _


def execute(filters=None):
    filters = filters or {}
    return get_columns(), get_data(filters)


def get_columns():
    return [
        {"label": _("Return"), "fieldname": "name", "fieldtype": "Link", "options": "Asset Return", "width": 130},
        {"label": _("Employee"), "fieldname": "employee", "fieldtype": "Link", "options": "Employee", "width": 140},
        {"label": _("Asset"), "fieldname": "company_asset", "fieldtype": "Link", "options": "Company Asset", "width": 180},
        {"label": _("Employee Asset Category"), "fieldname": "asset_category", "fieldtype": "Link", "options": "Employee Asset Category", "width": 160},
        {"label": _("Return Date"), "fieldname": "return_date", "fieldtype": "Date", "width": 110},
        {"label": _("Disposition"), "fieldname": "disposition", "fieldtype": "Data", "width": 110},
        {"label": _("Penalty"), "fieldname": "penalty_amount", "fieldtype": "Currency", "width": 110}
    ]


def get_data(filters):
    conditions = ["ar.docstatus = 1", "ar.condition_at_return = 'Damaged'"]
    values = {}

    if filters.get("employee"):
        conditions.append("ar.employee = %(employee)s")
        values["employee"] = filters["employee"]
    if filters.get("asset_category"):
        conditions.append("ca.asset_category = %(asset_category)s")
        values["asset_category"] = filters["asset_category"]
    if filters.get("disposition"):
        conditions.append("ar.disposition = %(disposition)s")
        values["disposition"] = filters["disposition"]

    return frappe.db.sql(
        f"""
        SELECT
            ar.name,
            ar.employee,
            ar.company_asset,
            ca.asset_category,
            ar.return_date,
            ar.disposition,
            ar.penalty_amount
        FROM `tabAsset Return` ar
        INNER JOIN `tabCompany Asset` ca ON ca.name = ar.company_asset
        WHERE {' AND '.join(conditions)}
        ORDER BY ar.return_date DESC
        """,
        values,
        as_dict=1,
    )
