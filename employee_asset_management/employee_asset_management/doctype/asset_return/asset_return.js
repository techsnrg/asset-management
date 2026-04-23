frappe.ui.form.on("Asset Return", {
    setup(frm) {
        frm.set_query("asset_assignment", () => ({
            filters: {
                docstatus: 1,
                assignment_status: "Active"
            }
        }));
    },

    refresh(frm) {
        frm.trigger("condition_at_return");
    },

    asset_assignment(frm) {
        if (!frm.doc.asset_assignment) {
            return;
        }

        frappe.db.get_doc("Asset Assignment", frm.doc.asset_assignment).then((doc) => {
            frm.set_value("employee", doc.employee);
            frm.set_value("company_asset", doc.company_asset);
        });
    },

    condition_at_return(frm) {
        const isDamaged = frm.doc.condition_at_return === "Damaged";
        frm.set_df_property("penalty_amount", "hidden", !isDamaged);
        frm.set_df_property("damage_notes", "reqd", isDamaged);
        frm.set_df_property("damage_photo", "hidden", !isDamaged);
        if (isDamaged) {
            frm.set_value("disposition", "Maintenance");
        } else if (!frm.doc.disposition || frm.doc.disposition === "Maintenance") {
            frm.set_value("disposition", "Available");
        }
    }
});
