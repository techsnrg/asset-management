import frappe
from frappe import _
from frappe.model.document import Document


class AssetCategory(Document):
    def validate(self):
        if self.requires_approval and not self.auto_approve and not self.use_default_approver:
            if not self.approver_role and not self.approver_user:
                frappe.throw(_("Select an approver role or approver user when not using the default approver."))

        if not self.allowed_issuer_roles:
            frappe.throw(_("Add at least one allowed issuer role for this asset category."))
