import frappe
from frappe import _
from frappe.utils import date_diff, getdate, today

from employee_asset_management.employee_asset_management.utils import (
    get_overdue_repeat_days,
    get_reminder_days_before_due,
    send_notification,
)


def send_due_reminders():
    reminder_days = get_reminder_days_before_due()
    overdue_repeat_days = get_overdue_repeat_days()
    current_date = getdate(today())

    assignments = frappe.get_all(
        "Asset Assignment",
        filters={
            "docstatus": 1,
            "assignment_status": "Active",
            "expected_return_date": ["is", "set"],
        },
        fields=[
            "name",
            "employee",
            "company_asset",
            "expected_return_date",
            "assigned_by",
        ],
    )

    for assignment in assignments:
        expected_return_date = getdate(assignment.expected_return_date)
        days_until_due = date_diff(expected_return_date, current_date)

        if days_until_due == reminder_days:
            _notify_due_soon(assignment)
            continue

        if days_until_due < 0 and abs(days_until_due) % overdue_repeat_days == 0:
            _notify_overdue(assignment, abs(days_until_due))


def _notify_due_soon(assignment):
    employee_user = frappe.db.get_value("Employee", assignment.employee, "user_id")
    recipients = [employee_user, assignment.assigned_by]
    subject = _("Asset Return Due Soon: {0}").format(assignment.company_asset)
    message = _(
        "Asset {0} assigned to {1} is due for return on {2}."
    ).format(assignment.company_asset, assignment.employee, assignment.expected_return_date)
    send_notification(recipients, subject, message, "Asset Assignment", assignment.name)


def _notify_overdue(assignment, overdue_days):
    employee_user = frappe.db.get_value("Employee", assignment.employee, "user_id")
    recipients = [employee_user, assignment.assigned_by]
    subject = _("Overdue Asset Return: {0}").format(assignment.company_asset)
    message = _(
        "Asset {0} assigned to {1} is overdue by {2} day(s). Expected return date was {3}."
    ).format(
        assignment.company_asset,
        assignment.employee,
        overdue_days,
        assignment.expected_return_date,
    )
    send_notification(recipients, subject, message, "Asset Assignment", assignment.name)
