import frappe
from frappe import _
from frappe.model.document import Document


class EmployeeAssetCategory(Document):
    def validate(self):
        if self.low_stock_threshold and int(self.low_stock_threshold) < 0:
            frappe.throw(_("Low stock threshold cannot be negative."))

        if self.requires_approval and not self.auto_approve and not self.use_default_approver:
            if not self.approver_role and not self.approver_user and not self.approval_matrix_rules:
                frappe.throw(_("Select an approver role or approver user when not using the default approver."))

        for row in self.approval_matrix_rules or []:
            if not row.approver_role and not row.approver_user:
                frappe.throw(_("Each approval matrix rule must define an approver role or approver user."))
            if row.minimum_value and row.maximum_value and row.minimum_value > row.maximum_value:
                frappe.throw(_("Approval matrix rule minimum value cannot be greater than maximum value."))

        if not self.allowed_issuer_roles:
            frappe.throw(_("Add at least one allowed issuer role for this asset category."))
