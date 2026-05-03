frappe.ui.form.on("Employee Sample Issue", {
    onload(frm) {
        if (frm.is_new() && frm.doc.delivery_note && !has_loaded_items(frm)) {
            load_delivery_note_items(frm);
        }
    },

    delivery_note(frm) {
        if (!frm.doc.delivery_note) {
            frm.clear_table("items");
            frm.refresh_field("items");
            return;
        }

        load_delivery_note_items(frm);
    },

    refresh(frm) {
        frm.set_intro(__("This record is created from a submitted Delivery Note and tracks employee sample accountability."));
    }
});

function load_delivery_note_items(frm) {
    frappe.call({
        method: "employee_asset_management.employee_asset_management.doctype.employee_sample_issue.employee_sample_issue.get_sample_issue_data_from_delivery_note",
        args: {
            delivery_note_name: frm.doc.delivery_note
        },
        freeze: true,
        freeze_message: __("Loading delivery note items"),
        callback(r) {
            const data = r.message;
            if (!data) {
                return;
            }

            if (data.existing_issue && (!frm.doc.name || frm.doc.__islocal)) {
                frappe.show_alert({
                    message: __("Sample Issue {0} already exists for this Delivery Note", [data.existing_issue]),
                    indicator: "orange"
                });
            }

            frm.set_value("employee", data.employee || "");
            frm.set_value("company", data.company || "");
            frm.set_value("issue_date", data.issue_date || "");

            frm.clear_table("items");
            (data.items || []).forEach((item) => {
                const row = frm.add_child("items");
                Object.assign(row, item);
            });
            frm.refresh_field("items");
        }
    });
}

function has_loaded_items(frm) {
    return Boolean((frm.doc.items || []).some((row) => row.item_code));
}
