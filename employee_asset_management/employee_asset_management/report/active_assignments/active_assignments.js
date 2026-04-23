frappe.query_reports["Active Assignments"] = {
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
        }
    ]
};
