frappe.ui.form.on("Employee Sample Issue", {
    refresh(frm) {
        frm.set_intro(__("This record is created from a submitted Delivery Note and tracks employee sample accountability."));
    }
});
