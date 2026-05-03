import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt

from employee_asset_management.employee_asset_management.utils import get_employee_for_user, has_any_role


class EmployeeSampleIssue(Document):
    def before_validate(self):
        if not self.issued_by:
            self.issued_by = frappe.session.user
        if not self.issue_date:
            self.issue_date = frappe.utils.today()

    def validate(self):
        if not self.items:
            frappe.throw(_("Add at least one sample item."))

        self.set_totals_and_status()

    def set_totals_and_status(self):
        total_qty = 0
        total_returned_qty = 0
        total_outstanding_qty = 0
        total_issue_value = 0
        total_outstanding_value = 0

        for row in self.items:
            row.qty_issued = flt(row.qty_issued)
            row.qty_returned = flt(row.qty_returned)
            row.rate = flt(row.rate)
            row.line_value = flt(row.line_value) or row.qty_issued * row.rate

            if row.qty_returned < 0:
                frappe.throw(_("Returned quantity cannot be negative for item {0}.").format(row.item_code))
            if row.qty_returned > row.qty_issued:
                frappe.throw(
                    _("Returned quantity cannot exceed issued quantity for item {0}.").format(row.item_code)
                )

            row.qty_pending = flt(row.qty_issued - row.qty_returned)
            row.outstanding_value = flt(
                (row.line_value / row.qty_issued) * row.qty_pending if row.qty_issued else 0
            )

            if row.qty_returned == 0:
                row.line_status = "Open"
            elif row.qty_pending == 0:
                row.line_status = "Returned"
            else:
                row.line_status = "Partially Returned"

            total_qty += row.qty_issued
            total_returned_qty += row.qty_returned
            total_outstanding_qty += row.qty_pending
            total_issue_value += row.line_value
            total_outstanding_value += row.outstanding_value

        self.total_qty = total_qty
        self.total_returned_qty = total_returned_qty
        self.total_outstanding_qty = total_outstanding_qty
        self.total_issue_value = total_issue_value
        self.total_outstanding_value = total_outstanding_value

        if total_outstanding_qty == 0:
            self.status = "Closed"
        elif total_returned_qty > 0:
            self.status = "Partially Returned"
        else:
            self.status = "Open"


def build_sample_issue_payload(delivery_note):
    payload = {
        "employee": getattr(delivery_note, "custom_employee_name", None),
        "company": delivery_note.company,
        "issue_date": delivery_note.posting_date,
        "items": [],
    }

    for item in delivery_note.items:
        qty = flt(item.qty)
        if qty <= 0:
            continue

        line_value = flt(item.amount) or qty * flt(item.rate)
        payload["items"].append(
            {
                "item_code": item.item_code,
                "item_name": item.item_name,
                "description": item.description,
                "warehouse": item.warehouse,
                "uom": item.uom,
                "qty_issued": qty,
                "qty_returned": 0,
                "rate": flt(item.rate),
                "line_value": line_value,
                "remarks": "",
            }
        )

    return payload


def validate_delivery_note_for_sample_issue(delivery_note):
    if not frappe.has_permission("Delivery Note", "read", doc=delivery_note):
        frappe.throw(_("You do not have permission to access this Delivery Note."))
    if delivery_note.docstatus != 1:
        frappe.throw(_("Sample Issue can only be created from a submitted Delivery Note."))
    if getattr(delivery_note, "is_return", 0):
        frappe.throw(_("Sample Issue cannot be created from a return Delivery Note."))
    if not getattr(delivery_note, "custom_employee_name", None):
        frappe.throw(_("Please fill Employee Name on the Delivery Note before creating a Sample Issue."))


def get_existing_sample_issue(delivery_note_name):
    return frappe.db.get_value(
        "Employee Sample Issue",
        {"delivery_note": delivery_note_name, "docstatus": ["<", 2]},
        "name",
    )


@frappe.whitelist()
def get_sample_issue_data_from_delivery_note(delivery_note_name):
    delivery_note = frappe.get_doc("Delivery Note", delivery_note_name)
    validate_delivery_note_for_sample_issue(delivery_note)

    existing = get_existing_sample_issue(delivery_note.name)
    payload = build_sample_issue_payload(delivery_note)
    payload["existing_issue"] = existing
    return payload


@frappe.whitelist()
def create_sample_issue_from_delivery_note(delivery_note_name):
    delivery_note = frappe.get_doc("Delivery Note", delivery_note_name)
    validate_delivery_note_for_sample_issue(delivery_note)

    existing = get_existing_sample_issue(delivery_note.name)
    if existing:
        return {"name": existing, "created": False}

    payload = build_sample_issue_payload(delivery_note)
    issue = frappe.get_doc(
        {
            "doctype": "Employee Sample Issue",
            "employee": payload["employee"],
            "delivery_note": delivery_note.name,
            "company": payload["company"],
            "issue_date": payload["issue_date"],
            "issued_by": frappe.session.user,
        }
    )

    for item in payload["items"]:
        issue.append("items", item)

    if not issue.items:
        frappe.throw(_("Delivery Note does not contain any issueable items."))

    issue.insert(ignore_permissions=True)
    return {"name": issue.name, "created": True}
