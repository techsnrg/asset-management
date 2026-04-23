frappe.ui.form.on("Delivery Note", {
    refresh(frm) {
        if (!can_create_sample_issue(frm)) {
            return;
        }

        frm.add_custom_button(__("Sample Issue"), () => {
            frappe.call({
                method: "employee_asset_management.employee_asset_management.doctype.employee_sample_issue.employee_sample_issue.create_sample_issue_from_delivery_note",
                args: {
                    delivery_note_name: frm.doc.name
                },
                freeze: true,
                freeze_message: __("Preparing employee sample issue"),
                callback(r) {
                    if (!r.message || !r.message.name) {
                        return;
                    }

                    if (r.message.created) {
                        frappe.show_alert({
                            message: __("Employee Sample Issue {0} created", [r.message.name]),
                            indicator: "green"
                        });
                    }

                    frappe.set_route("Form", "Employee Sample Issue", r.message.name);
                }
            });
        }, __("Create"));
    }
});

function can_create_sample_issue(frm) {
    return Boolean(
        frm.doc.docstatus === 1 &&
        !frm.doc.is_return &&
        frm.doc.custom_employee_name &&
        frm.doc.items &&
        frm.doc.items.length
    );
}
