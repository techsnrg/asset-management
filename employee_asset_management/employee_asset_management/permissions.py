import frappe

from employee_asset_management.employee_asset_management.utils import (
    PRIVILEGED_ROLES,
    get_employee_for_user,
    has_any_role,
)


def asset_request_query(user):
    if has_any_role(user, PRIVILEGED_ROLES):
        return None

    employee = get_employee_for_user(user)
    conditions = ["`tabAsset Request`.`requested_by` = {0}".format(frappe.db.escape(user))]
    if employee:
        conditions.append("`tabAsset Request`.`requested_for` = {0}".format(frappe.db.escape(employee)))
    return " OR ".join(f"({condition})" for condition in conditions)


def asset_request_has_permission(doc, user=None, permission_type=None):
    user = user or frappe.session.user
    if has_any_role(user, PRIVILEGED_ROLES):
        return True

    employee = get_employee_for_user(user)
    return doc.requested_by == user or bool(employee and doc.requested_for == employee)


def asset_assignment_query(user):
    if has_any_role(user, PRIVILEGED_ROLES):
        return None

    employee = get_employee_for_user(user)
    if not employee:
        return "1=0"
    return "`tabAsset Assignment`.`employee` = {0}".format(frappe.db.escape(employee))


def asset_assignment_has_permission(doc, user=None, permission_type=None):
    user = user or frappe.session.user
    if has_any_role(user, PRIVILEGED_ROLES):
        return True

    employee = get_employee_for_user(user)
    return bool(employee and doc.employee == employee)


def asset_return_query(user):
    if has_any_role(user, PRIVILEGED_ROLES):
        return None

    employee = get_employee_for_user(user)
    if not employee:
        return "1=0"
    return "`tabAsset Return`.`employee` = {0}".format(frappe.db.escape(employee))


def asset_return_has_permission(doc, user=None, permission_type=None):
    user = user or frappe.session.user
    if has_any_role(user, PRIVILEGED_ROLES):
        return True

    employee = get_employee_for_user(user)
    return bool(employee and doc.employee == employee)


def company_asset_query(user):
    if has_any_role(user, PRIVILEGED_ROLES):
        return None

    employee = get_employee_for_user(user)
    if not employee:
        return "1=0"
    return "`tabCompany Asset`.`current_holder` = {0}".format(frappe.db.escape(employee))


def company_asset_has_permission(doc, user=None, permission_type=None):
    user = user or frappe.session.user
    if has_any_role(user, PRIVILEGED_ROLES):
        return True

    employee = get_employee_for_user(user)
    return bool(employee and doc.current_holder == employee)


def employee_sample_issue_query(user):
    if has_any_role(user, PRIVILEGED_ROLES):
        return None

    employee = get_employee_for_user(user)
    if not employee:
        return "1=0"
    return "`tabEmployee Sample Issue`.`employee` = {0}".format(frappe.db.escape(employee))


def employee_sample_issue_has_permission(doc, user=None, permission_type=None):
    user = user or frappe.session.user
    if has_any_role(user, PRIVILEGED_ROLES):
        return True

    employee = get_employee_for_user(user)
    if employee and doc.employee == employee:
        return True

    if doc.delivery_note:
        try:
            delivery_note = frappe.get_doc("Delivery Note", doc.delivery_note)
        except frappe.DoesNotExistError:
            delivery_note = None

        if delivery_note and frappe.has_permission("Delivery Note", "read", doc=delivery_note, user=user):
            return True

    return False
