frappe.ui.form.on("Asset Request", {
    setup(frm) {
        frm.set_query("requested_for", () => ({
            filters: {
                status: "Active"
            }
        }));
    },

    onload(frm) {
        if (frm.is_new() && !frm.doc.requested_by) {
            frm.set_value("requested_by", frappe.session.user);
        }
    },

    requested_for(frm) {
        if (!frm.doc.requested_for) {
            frm.set_value("department", "");
            return;
        }

        frappe.db.get_value("Employee", frm.doc.requested_for, "department").then(({ message }) => {
            frm.set_value("department", (message && message.department) || "");
        });
    },

    refresh(frm) {
        if (!frm.is_new() && frm.doc.docstatus === 1 && frm.doc.status === "Pending Approval") {
            if (frm.doc.approver === frappe.session.user || frappe.user.has_role("System Manager")) {
                frm.add_custom_button(__("Approve"), () => {
                    review_request(frm, "approve_request", "Approve Request");
                }, __("Actions"));
                frm.add_custom_button(__("Reject"), () => {
                    review_request(frm, "reject_request", "Reject Request");
                }, __("Actions"));
            }
        }
    }
});

function review_request(frm, method, title) {
    frappe.prompt(
        [
            {
                fieldname: "remarks",
                fieldtype: "Small Text",
                label: __("Remarks")
            }
        ],
        (values) => {
            frappe.call({
                method: "employee_asset_management.employee_asset_management.doctype.asset_request.asset_request." + method,
                args: {
                    docname: frm.doc.name,
                    remarks: values.remarks || ""
                },
                freeze: true,
                freeze_message: __(title),
                callback() {
                    frm.reload_doc();
                }
            });
        },
        title,
        __("Submit")
    );
}
