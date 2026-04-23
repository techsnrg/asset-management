frappe.ui.form.on("Asset Assignment", {
    setup(frm) {
        frm.set_query("asset_request", () => ({
            filters: {
                docstatus: 1,
                status: "Approved"
            }
        }));

        frm.set_query("company_asset", () => {
            const filters = {
                current_status: "Available"
            };

            if (frm.asset_request_category) {
                filters.asset_category = frm.asset_request_category;
            }

            return { filters };
        });
    },

    asset_request(frm) {
        if (!frm.doc.asset_request) {
            return;
        }

        frappe.db.get_doc("Asset Request", frm.doc.asset_request).then((doc) => {
            frm.asset_request_category = doc.asset_category;
            frm.set_value("employee", doc.requested_for);
            frm.set_query("company_asset", () => ({
                filters: {
                    current_status: "Available",
                    asset_category: doc.asset_category
                }
            }));
        });
    },

    refresh(frm) {
        if (
            frm.doc.docstatus === 1 &&
            frm.doc.assignment_status === "Active" &&
            !frm.doc.asset_acknowledged_by_employee
        ) {
            frm.add_custom_button(__("Acknowledge Receipt"), () => {
                frappe.call({
                    method: "employee_asset_management.employee_asset_management.doctype.asset_assignment.asset_assignment.acknowledge_assignment",
                    args: {
                        docname: frm.doc.name
                    },
                    freeze: true,
                    freeze_message: __("Acknowledging asset receipt"),
                    callback() {
                        frm.reload_doc();
                    }
                });
            }, __("Actions"));
        }
    }
});
