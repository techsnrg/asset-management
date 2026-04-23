frappe.query_reports["Damaged Returns"] = {
    filters: [
        {
            fieldname: "employee",
            label: __("Employee"),
            fieldtype: "Link",
            options: "Employee"
        },
        {
            fieldname: "asset_category",
            label: __("Asset Category"),
            fieldtype: "Link",
            options: "Asset Category"
        },
        {
            fieldname: "disposition",
            label: __("Disposition"),
            fieldtype: "Select",
            options: "\nMaintenance\nRetired"
        }
    ]
};
