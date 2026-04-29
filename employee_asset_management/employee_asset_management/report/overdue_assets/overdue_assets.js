frappe.query_reports["Overdue Assets"] = {
    filters: [
        {
            fieldname: "employee",
            label: __("Employee"),
            fieldtype: "Link",
            options: "Employee"
        },
        {
            fieldname: "asset_category",
            label: __("Employee Asset Category"),
            fieldtype: "Link",
            options: "Employee Asset Category"
        }
    ]
};
