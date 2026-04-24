import frappe
from frappe import _
from frappe.model.document import Document

from employee_asset_management.employee_asset_management.utils import (
    count_active_assignments,
    get_allowed_on_behalf_roles,
    get_employee_for_user,
    get_resolved_approver_for_category,
    has_any_role,
    send_notification,
)


class AssetRequest(Document):
    def before_validate(self):
        if not self.requested_by:
            self.requested_by = frappe.session.user
        if not self.status:
            self.status = "Draft"

    def validate(self):
        self.validate_requested_for()
        self.set_department()
        self.set_request_type()
        self.validate_on_behalf_request()
        self.validate_duplicate_open_request()
        self.check_limits()
        self.resolve_approver()

    def before_submit(self):
        category = frappe.get_cached_doc("Asset Category", self.asset_category)
        if not category.requires_approval or category.auto_approve:
            self.status = "Approved"
            if not self.approved_by:
                self.approved_by = self.requested_by
            if not self.approval_remarks:
                self.approval_remarks = _("Auto-approved as per category policy.")
        else:
            self.status = "Pending Approval"

    def on_submit(self):
        if self.status == "Pending Approval":
            self.notify_approver()
        elif self.status == "Approved":
            self.notify_request_outcome()

    def on_cancel(self):
        frappe.db.set_value(self.doctype, self.name, "status", "Cancelled", update_modified=False)

    def set_request_type(self):
        requester_employee = get_employee_for_user(self.requested_by)
        if self.request_type != "New Joiner":
            self.request_type = "Self" if requester_employee == self.requested_for else "On Behalf"

        if self.request_type == "Self" and requester_employee and requester_employee != self.requested_for:
            frappe.throw(_("Self requests must be created for your own employee record."))

    def validate_on_behalf_request(self):
        requester_employee = get_employee_for_user(self.requested_by)
        if requester_employee == self.requested_for:
            return

        allowed_roles = get_allowed_on_behalf_roles()
        if not has_any_role(self.requested_by, allowed_roles):
            frappe.throw(
                _("Only users with one of these roles can request on behalf of another employee: {0}").format(
                    ", ".join(allowed_roles)
                )
            )

    def validate_requested_for(self):
        employee_status = frappe.db.get_value("Employee", self.requested_for, "status")
        if employee_status and employee_status != "Active":
            frappe.throw(_("Asset requests can only be created for active employees."))

    def set_department(self):
        employee_department = frappe.db.get_value("Employee", self.requested_for, "department")
        self.department = employee_department or None

    def validate_duplicate_open_request(self):
        existing = frappe.db.exists(
            "Asset Request",
            {
                "name": ["!=", self.name],
                "requested_for": self.requested_for,
                "asset_category": self.asset_category,
                "status": ["in", ("Draft", "Pending Approval", "Approved")],
                "docstatus": ["<", 2],
            },
        )
        if existing:
            frappe.throw(
                _("An open request already exists for employee {0} and asset category {1}.").format(
                    self.requested_for, self.asset_category
                )
            )

    def resolve_approver(self):
        approver = get_resolved_approver_for_category(
            self.asset_category,
            department=self.department,
            urgency=self.urgency,
            estimated_value=self.estimated_value,
        )
        self.approver = approver

        category = frappe.get_cached_doc("Asset Category", self.asset_category)
        if category.requires_approval and not category.auto_approve and not self.approver:
            frappe.throw(_("No approver could be resolved for asset category {0}.").format(self.asset_category))

    def check_limits(self):
        max_allowed = frappe.db.get_value("Asset Category", self.asset_category, "max_per_employee")
        if max_allowed and count_active_assignments(self.requested_for, self.asset_category) >= int(max_allowed):
            frappe.throw(
                _("Employee already has the maximum allowed {0}. Limit: {1}").format(
                    self.asset_category, max_allowed
                )
            )

    def notify_approver(self):
        if not self.approver:
            return

        subject = _("New Asset Request: {0}").format(self.name)
        message = _("User {0} requested {1} for employee {2}.").format(
            self.requested_by, self.asset_category, self.requested_for
        )
        if self.department:
            message += _(" Department: {0}.").format(self.department)
        if self.estimated_value:
            message += _(" Estimated value: {0}.").format(self.estimated_value)
        message += _(" Please review the request.")
        send_notification([self.approver], subject, message, self.doctype, self.name)

    def notify_request_outcome(self):
        recipients = [self.requested_by]
        employee_user = frappe.db.get_value("Employee", self.requested_for, "user_id")
        if employee_user:
            recipients.append(employee_user)

        subject = _("Asset Request {0}: {1}").format(self.status, self.name)
        message = _("Request for {0} has been marked as {1}.").format(self.asset_category, self.status)
        if self.approval_remarks:
            message += _("<br>Remarks: {0}").format(self.approval_remarks)

        send_notification(recipients, subject, message, self.doctype, self.name)

    def ensure_can_approve(self, user):
        if has_any_role(user, {"System Manager"}):
            return
        if user != self.approver:
            frappe.throw(_("Only the resolved approver can review this request."))


@frappe.whitelist()
def approve_request(docname, remarks=None):
    doc = frappe.get_doc("Asset Request", docname)
    doc.ensure_can_approve(frappe.session.user)

    if doc.docstatus != 1 or doc.status != "Pending Approval":
        frappe.throw(_("Only pending approval requests can be approved."))

    frappe.db.set_value(
        "Asset Request",
        docname,
        {
            "status": "Approved",
            "approved_by": frappe.session.user,
            "approval_remarks": remarks or "",
        },
    )
    doc.reload()
    doc.notify_request_outcome()
    return doc


@frappe.whitelist()
def reject_request(docname, remarks=None):
    doc = frappe.get_doc("Asset Request", docname)
    doc.ensure_can_approve(frappe.session.user)

    if doc.docstatus != 1 or doc.status != "Pending Approval":
        frappe.throw(_("Only pending approval requests can be rejected."))

    frappe.db.set_value(
        "Asset Request",
        docname,
        {
            "status": "Rejected",
            "approved_by": frappe.session.user,
            "approval_remarks": remarks or "",
        },
    )
    doc.reload()
    doc.notify_request_outcome()
    return doc
