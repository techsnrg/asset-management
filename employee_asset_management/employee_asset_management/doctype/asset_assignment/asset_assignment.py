import frappe
from frappe import _
from frappe.model.document import Document

from employee_asset_management.employee_asset_management.utils import (
    count_active_assignments,
    ensure_user_can_issue_category,
    send_notification,
)


class AssetAssignment(Document):
    def before_validate(self):
        if not self.assigned_by:
            self.assigned_by = frappe.session.user
        if not self.assignment_status:
            self.assignment_status = "Active"
        if self.asset_request:
            self.employee = frappe.db.get_value("Asset Request", self.asset_request, "requested_for")

    def validate(self):
        self.validate_request()
        self.validate_issuer_role()
        self.validate_availability()
        self.check_category_limit()
        self.check_overlap()
        self.validate_expected_return_date()

    def validate_request(self):
        if not self.asset_request:
            frappe.throw(_("Asset Assignment must be created against an approved asset request."))

        request = frappe.get_doc("Asset Request", self.asset_request)
        asset_category = frappe.db.get_value("Company Asset", self.company_asset, "asset_category")

        if request.docstatus != 1 or request.status != "Approved":
            frappe.throw(_("Only approved asset requests can be fulfilled."))

        if request.requested_for != self.employee:
            frappe.throw(_("The assignment employee must match the employee on the asset request."))

        if request.asset_category != asset_category:
            frappe.throw(_("Selected asset must belong to the same category as the approved request."))

    def validate_issuer_role(self):
        category = frappe.db.get_value("Company Asset", self.company_asset, "asset_category")
        ensure_user_can_issue_category(category, frappe.session.user)

    def validate_availability(self):
        status = frappe.db.get_value("Company Asset", self.company_asset, "current_status")
        if status != "Available":
            current_holder = frappe.db.get_value("Company Asset", self.company_asset, "current_holder")
            if current_holder:
                frappe.throw(_("This asset is already assigned to {0}").format(current_holder))
            frappe.throw(_("Asset status is '{0}'. Only available assets can be assigned.").format(status))

    def check_category_limit(self):
        category = frappe.db.get_value("Company Asset", self.company_asset, "asset_category")
        max_allowed = frappe.db.get_value("Employee Asset Category", category, "max_per_employee")
        if max_allowed and count_active_assignments(self.employee, category, exclude_assignment=self.name) >= int(
            max_allowed
        ):
            frappe.throw(_("Employee already has maximum allowed {0}. Limit: {1}").format(category, max_allowed))

    def check_overlap(self):
        overlap = frappe.db.exists(
            "Asset Assignment",
            {
                "company_asset": self.company_asset,
                "name": ["!=", self.name],
                "docstatus": 1,
                "assignment_status": "Active",
            },
        )
        if overlap:
            frappe.throw(_("Asset {0} is already assigned to another active assignment.").format(self.company_asset))

    def validate_expected_return_date(self):
        if self.expected_return_date and self.expected_return_date < self.assigned_date:
            frappe.throw(_("Expected return date cannot be earlier than the assigned date."))

    def on_submit(self):
        frappe.db.set_value(
            "Company Asset",
            self.company_asset,
            {
                "current_status": "Assigned",
                "current_holder": self.employee,
            },
        )
        frappe.db.set_value("Asset Request", self.asset_request, "status", "Fulfilled")
        self.notify_employee()

    def on_cancel(self):
        if self.assignment_status == "Returned":
            frappe.throw(_("Returned assignments cannot be cancelled."))

        frappe.db.set_value(
            "Company Asset",
            self.company_asset,
            {
                "current_status": "Available",
                "current_holder": None,
            },
        )
        if self.asset_request:
            frappe.db.set_value("Asset Request", self.asset_request, "status", "Approved")

    def notify_employee(self):
        employee_user_id = frappe.db.get_value("Employee", self.employee, "user_id")
        if not employee_user_id:
            return

        subject = _("Asset Assigned: {0}").format(self.company_asset)
        message = _("A {0} ({1}) has been assigned to you. Expected return date: {2}.").format(
            frappe.db.get_value("Company Asset", self.company_asset, "asset_category"),
            self.company_asset,
            self.expected_return_date,
        )
        send_notification([employee_user_id], subject, message, self.doctype, self.name)


@frappe.whitelist()
def acknowledge_assignment(docname):
    doc = frappe.get_doc("Asset Assignment", docname)
    employee_user = frappe.db.get_value("Employee", doc.employee, "user_id")

    if frappe.session.user != employee_user:
        frappe.throw(_("Only the employee assigned to this asset can acknowledge receipt."))
    if doc.assignment_status != "Active" or doc.docstatus != 1:
        frappe.throw(_("Only active assignments can be acknowledged."))

    frappe.db.set_value(
        "Asset Assignment",
        docname,
        {
            "asset_acknowledged_by_employee": 1,
            "acknowledged_on": frappe.utils.now_datetime(),
        },
    )
    return frappe.get_doc("Asset Assignment", docname)
