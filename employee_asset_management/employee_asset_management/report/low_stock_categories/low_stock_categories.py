import frappe
from frappe import _
from frappe.utils import cint


def execute(filters=None):
    filters = filters or {}
    return get_columns(), get_data(filters)


def get_columns():
    return [
        {
            "label": _("Asset Category"),
            "fieldname": "asset_category",
            "fieldtype": "Link",
            "options": "Asset Category",
            "width": 180,
        },
        {"label": _("Low Stock Threshold"), "fieldname": "low_stock_threshold", "fieldtype": "Int", "width": 130},
        {"label": _("Available Assets"), "fieldname": "available_assets", "fieldtype": "Int", "width": 120},
        {"label": _("Assigned Assets"), "fieldname": "assigned_assets", "fieldtype": "Int", "width": 120},
        {"label": _("Maintenance Assets"), "fieldname": "maintenance_assets", "fieldtype": "Int", "width": 130},
        {"label": _("Total Assets"), "fieldname": "total_assets", "fieldtype": "Int", "width": 110},
        {"label": _("Shortage"), "fieldname": "shortage", "fieldtype": "Int", "width": 100},
    ]


def get_data(filters):
    conditions = ["ac.low_stock_threshold > 0"]
    values = {}

    if filters.get("asset_category"):
        conditions.append("ac.name = %(asset_category)s")
        values["asset_category"] = filters["asset_category"]

    rows = frappe.db.sql(
        f"""
        SELECT
            ac.name AS asset_category,
            ac.low_stock_threshold,
            COALESCE(SUM(CASE WHEN ca.current_status = 'Available' THEN 1 ELSE 0 END), 0) AS available_assets,
            COALESCE(SUM(CASE WHEN ca.current_status = 'Assigned' THEN 1 ELSE 0 END), 0) AS assigned_assets,
            COALESCE(SUM(CASE WHEN ca.current_status = 'Maintenance' THEN 1 ELSE 0 END), 0) AS maintenance_assets,
            COUNT(ca.name) AS total_assets
        FROM `tabAsset Category` ac
        LEFT JOIN `tabCompany Asset` ca ON ca.asset_category = ac.name
        WHERE {' AND '.join(conditions)}
        GROUP BY ac.name, ac.low_stock_threshold
        ORDER BY ac.name ASC
        """,
        values,
        as_dict=1,
    )

    show_all = cint(filters.get("show_all_threshold_categories"))
    data = []
    for row in rows:
        row.shortage = max(cint(row.low_stock_threshold) - cint(row.available_assets), 0)
        if show_all or row.available_assets <= row.low_stock_threshold:
            data.append(row)

    return sorted(data, key=lambda row: (-row.shortage, row.asset_category))
