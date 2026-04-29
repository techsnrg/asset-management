import frappe
from frappe import _
from frappe.utils import flt


DEFAULT_ON_BEHALF_ROLES = ("HR User", "HR Manager", "Admin", "System Manager")
PRIVILEGED_ROLES = {
    "System Manager",
    "HR Manager",
    "HR User",
    "Admin",
    "IT Manager",
    "Managing Director",
}


def get_settings():
    return frappe.get_single("Asset Management Settings")


def get_employee_for_user(user=None):
    user = user or frappe.session.user
    if not user or user == "Guest":
        return None
    return frappe.db.get_value("Employee", {"user_id": user}, "name")


def get_allowed_on_behalf_roles():
    try:
        settings = get_settings()
        roles = [row.role for row in settings.allowed_on_behalf_requester_roles if row.role]
        return roles or list(DEFAULT_ON_BEHALF_ROLES)
    except frappe.DoesNotExistError:
        return list(DEFAULT_ON_BEHALF_ROLES)


def get_default_approver_role():
    try:
        return get_settings().default_approver_role or "Managing Director"
    except frappe.DoesNotExistError:
        return "Managing Director"


def get_damage_default_disposition():
    try:
        return get_settings().damage_default_disposition or "Maintenance"
    except frappe.DoesNotExistError:
        return "Maintenance"


def get_reminder_days_before_due():
    try:
        return cint_or_default(get_settings().reminder_days_before_due, 3)
    except frappe.DoesNotExistError:
        return 3


def get_overdue_repeat_days():
    try:
        return max(cint_or_default(get_settings().overdue_repeat_days, 2), 1)
    except frappe.DoesNotExistError:
        return 2


def cint_or_default(value, default):
    try:
        return int(value or default)
    except (TypeError, ValueError):
        return default


def has_any_role(user, roles):
    if not roles:
        return False
    user_roles = set(frappe.get_roles(user))
    return bool(user_roles.intersection(set(roles)))


def is_privileged_user(user=None):
    return has_any_role(user or frappe.session.user, PRIVILEGED_ROLES)


def get_users_for_role(role_name):
    if not role_name:
        return []

    return frappe.get_all(
        "Has Role",
        filters={"role": role_name, "parenttype": "User"},
        pluck="parent",
    )


def get_first_enabled_user_for_role(role_name):
    users = get_users_for_role(role_name)
    if not users:
        return None

    return frappe.db.get_value(
        "User",
        {"name": ["in", users], "enabled": 1},
        "name",
        order_by="name asc",
    )


def get_category_doc(category_name):
    return frappe.get_cached_doc("Employee Asset Category", category_name)


def get_category_issuer_roles(category_name):
    category = get_category_doc(category_name)
    return [row.role for row in category.allowed_issuer_roles if row.role]


def get_matching_approval_rule(category, department=None, urgency=None, estimated_value=0):
    estimated_value = flt(estimated_value)

    for row in category.approval_matrix_rules or []:
        if row.department and row.department != department:
            continue
        if row.urgency and row.urgency != urgency:
            continue

        minimum_value = flt(row.minimum_value)
        maximum_value = flt(row.maximum_value)

        if minimum_value and estimated_value < minimum_value:
            continue
        if maximum_value and estimated_value > maximum_value:
            continue
        if row.approver_user or row.approver_role:
            return row

    return None


def resolve_approver_from_rule(rule):
    if not rule:
        return None
    if rule.approver_user:
        return rule.approver_user
    if rule.approver_role:
        return get_first_enabled_user_for_role(rule.approver_role)
    return None


def get_resolved_approver_for_category(category_name, department=None, urgency=None, estimated_value=0):
    category = get_category_doc(category_name)

    if not category.requires_approval or category.auto_approve:
        return None

    matrix_rule = get_matching_approval_rule(
        category,
        department=department,
        urgency=urgency,
        estimated_value=estimated_value,
    )
    approver = resolve_approver_from_rule(matrix_rule)
    if approver:
        return approver

    if not category.use_default_approver:
        if category.approver_user:
            return category.approver_user
        if category.approver_role:
            approver = get_first_enabled_user_for_role(category.approver_role)
            if approver:
                return approver

    default_role = get_default_approver_role()
    return get_first_enabled_user_for_role(default_role)


def ensure_user_can_issue_category(category_name, user=None):
    user = user or frappe.session.user
    if has_any_role(user, {"System Manager"}):
        return

    issuer_roles = get_category_issuer_roles(category_name)
    if not issuer_roles:
        frappe.throw(
            _("No issuer role is configured for asset category {0}.").format(category_name)
        )

    if not has_any_role(user, issuer_roles):
        frappe.throw(
            _("Only users with one of these roles can issue assets in category {0}: {1}").format(
                category_name, ", ".join(issuer_roles)
            )
        )


def count_active_assignments(employee, asset_category, exclude_assignment=None):
    conditions = ["aa.employee = %(employee)s", "aa.docstatus = 1", "aa.assignment_status = 'Active'"]
    values = {"employee": employee, "asset_category": asset_category}

    if exclude_assignment:
        conditions.append("aa.name != %(exclude_assignment)s")
        values["exclude_assignment"] = exclude_assignment

    query = f"""
        SELECT COUNT(*)
        FROM `tabAsset Assignment` aa
        INNER JOIN `tabCompany Asset` ca ON ca.name = aa.company_asset
        WHERE {' AND '.join(conditions)}
          AND ca.asset_category = %(asset_category)s
    """
    return frappe.db.sql(query, values)[0][0]


def create_notification_logs(users, subject, document_type, document_name):
    for user in {user for user in users if user}:
        frappe.get_doc(
            {
                "doctype": "Notification Log",
                "subject": subject,
                "for_user": user,
                "type": "Alert",
                "document_type": document_type,
                "document_name": document_name,
            }
        ).insert(ignore_permissions=True)


def send_notification(users, subject, message, document_type, document_name):
    recipients = [user for user in set(users) if user]
    if not recipients:
        return

    frappe.sendmail(recipients=recipients, subject=subject, message=message)
    create_notification_logs(recipients, subject, document_type, document_name)
