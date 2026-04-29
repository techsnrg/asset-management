import frappe


SOURCE_DOCTYPE = "Asset Category"
TARGET_DOCTYPE = "Employee Asset Category"

SOURCE_FIELDS = (
    "name",
    "category_name",
    "requires_approval",
    "auto_approve",
    "max_per_employee",
    "low_stock_threshold",
    "use_default_approver",
    "approver_role",
    "approver_user",
)


def execute():
    if not frappe.db.exists("DocType", TARGET_DOCTYPE):
        return
    if not frappe.db.exists("DocType", SOURCE_DOCTYPE):
        return

    category_names = get_category_names_to_migrate()
    if not category_names:
        return

    available_columns = set(frappe.db.get_table_columns(SOURCE_DOCTYPE) or [])
    source_fields = [field for field in SOURCE_FIELDS if field in available_columns]
    if "name" not in source_fields:
        source_fields.insert(0, "name")

    for category_name in category_names:
        source_row = get_source_row(category_name, source_fields)
        if not source_row:
            continue

        target = get_or_create_target_doc(source_row)
        set_scalar_fields(target, source_row)
        set_child_rows(target, source_row["name"])
        save_target_doc(target)


def get_category_names_to_migrate():
    names = set()

    if frappe.db.exists("DocType", "Company Asset"):
        names.update(frappe.get_all("Company Asset", filters={"asset_category": ["is", "set"]}, pluck="asset_category"))
    if frappe.db.exists("DocType", "Asset Request"):
        names.update(frappe.get_all("Asset Request", filters={"asset_category": ["is", "set"]}, pluck="asset_category"))

    if frappe.db.table_exists("Asset Category Issuer Role"):
        names.update(
            row[0]
            for row in frappe.db.sql(
                """
                SELECT DISTINCT parent
                FROM `tabAsset Category Issuer Role`
                WHERE parenttype = %s
                """,
                (SOURCE_DOCTYPE,),
            )
            if row and row[0]
        )

    if frappe.db.table_exists("Asset Category Approval Rule"):
        names.update(
            row[0]
            for row in frappe.db.sql(
                """
                SELECT DISTINCT parent
                FROM `tabAsset Category Approval Rule`
                WHERE parenttype = %s
                """,
                (SOURCE_DOCTYPE,),
            )
            if row and row[0]
        )

    if not names:
        names.update(frappe.get_all(SOURCE_DOCTYPE, pluck="name"))

    return sorted(name for name in names if name)


def get_source_row(category_name, fields):
    field_sql = ", ".join(f"`{field}`" for field in fields)
    rows = frappe.db.sql(
        f"""
        SELECT {field_sql}
        FROM `tab{SOURCE_DOCTYPE}`
        WHERE name = %s
        """,
        (category_name,),
        as_dict=True,
    )
    return rows[0] if rows else None


def get_or_create_target_doc(source_row):
    target_name = source_row.get("category_name") or source_row["name"]

    if frappe.db.exists(TARGET_DOCTYPE, target_name):
        return frappe.get_doc(TARGET_DOCTYPE, target_name)

    doc = frappe.new_doc(TARGET_DOCTYPE)
    doc.category_name = target_name
    return doc


def set_scalar_fields(target, source_row):
    target.category_name = source_row.get("category_name") or source_row["name"]

    for field in (
        "requires_approval",
        "auto_approve",
        "max_per_employee",
        "low_stock_threshold",
        "use_default_approver",
        "approver_role",
        "approver_user",
    ):
        if field in source_row:
            setattr(target, field, source_row.get(field))


def set_child_rows(target, source_name):
    target.set("allowed_issuer_roles", [])
    if frappe.db.table_exists("Asset Category Issuer Role"):
        for row in frappe.db.sql(
            """
            SELECT role
            FROM `tabAsset Category Issuer Role`
            WHERE parent = %s AND parenttype = %s
            ORDER BY idx ASC
            """,
            (source_name, SOURCE_DOCTYPE),
            as_dict=True,
        ):
            if row.get("role"):
                target.append("allowed_issuer_roles", {"role": row["role"]})

    target.set("approval_matrix_rules", [])
    if frappe.db.table_exists("Asset Category Approval Rule"):
        for row in frappe.db.sql(
            """
            SELECT department, urgency, minimum_value, maximum_value, approver_role, approver_user
            FROM `tabAsset Category Approval Rule`
            WHERE parent = %s AND parenttype = %s
            ORDER BY idx ASC
            """,
            (source_name, SOURCE_DOCTYPE),
            as_dict=True,
        ):
            target.append("approval_matrix_rules", row)


def save_target_doc(target):
    if not target.allowed_issuer_roles:
        target.append("allowed_issuer_roles", {"role": "System Manager"})

    if (
        target.requires_approval
        and not target.auto_approve
        and not target.use_default_approver
        and not target.approver_role
        and not target.approver_user
        and not target.approval_matrix_rules
    ):
        target.use_default_approver = 1

    if target.is_new():
        target.insert(ignore_permissions=True)
    else:
        target.save(ignore_permissions=True)
