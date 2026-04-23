import frappe
from frappe import _
from frappe.model.document import Document

from employee_asset_management.employee_asset_management.utils import (
    ensure_user_can_issue_category,
    get_damage_default_disposition,
    get_users_for_role,
    send_notification,
)


class AssetReturn(Document):
    def before_validate(self):
        if not self.received_by:
            self.received_by = frappe.session.user

        if self.asset_assignment:
            assignment = frappe.get_doc("Asset Assignment", self.asset_assignment)
            self.employee = assignment.employee
            self.company_asset = assignment.company_asset

        if not self.disposition:
            self.disposition = (
                get_damage_default_disposition()
                if self.condition_at_return == "Damaged"
                else "Available"
            )

    def validate(self):
        self.validate_assignment()
        self.validate_receiver_role()
        self.validate_disposition()

    def validate_assignment(self):
        assignment = frappe.get_doc("Asset Assignment", self.asset_assignment)
        if assignment.docstatus != 1 or assignment.assignment_status != "Active":
            frappe.throw(_("Only active assignments can be returned."))

        if frappe.db.exists(
            "Asset Return",
            {
                "name": ["!=", self.name],
                "asset_assignment": self.asset_assignment,
                "docstatus": 1,
            },
        ):
            frappe.throw(_("A return has already been recorded for this assignment."))

    def validate_receiver_role(self):
        category = frappe.db.get_value("Company Asset", self.company_asset, "asset_category")
        ensure_user_can_issue_category(category, frappe.session.user)

    def validate_disposition(self):
        if self.condition_at_return == "Damaged" and self.disposition == "Available":
            frappe.throw(_("Damaged assets cannot be returned directly to Available status."))

    def on_submit(self):
        frappe.db.set_value("Asset Assignment", self.asset_assignment, "assignment_status", "Returned")
        frappe.db.set_value(
            "Company Asset",
            self.company_asset,
            {
                "current_status": self.disposition,
                "current_holder": None,
                "condition": self.condition_at_return,
            },
        )

        if self.condition_at_return == "Damaged":
            self.notify_admin_of_damage()

    def on_cancel(self):
        frappe.db.set_value("Asset Assignment", self.asset_assignment, "assignment_status", "Active")
        frappe.db.set_value(
            "Company Asset",
            self.company_asset,
            {
                "current_status": "Assigned",
                "current_holder": self.employee,
            },
        )

    def notify_admin_of_damage(self):
        admin_users = get_users_for_role("System Manager")
        if not admin_users:
            return

        subject = _("Asset Returned Damaged: {0}").format(self.company_asset)
        message = _("""
            <p>An asset has been returned in <b>Damaged</b> condition.</p>
            <ul>
                <li><b>Asset:</b> {0}</li>
                <li><b>Employee:</b> {1}</li>
                <li><b>Return Date:</b> {2}</li>
                <li><b>Notes:</b> {3}</li>
                <li><b>Penalty Amount:</b> {4}</li>
                <li><b>Disposition:</b> {5}</li>
            </ul>
        """).format(
            self.company_asset,
            self.employee,
            self.return_date,
            self.damage_notes or "No notes provided",
            self.penalty_amount or 0,
            self.disposition,
        )

        send_notification(admin_users, subject, message, self.doctype, self.name)
