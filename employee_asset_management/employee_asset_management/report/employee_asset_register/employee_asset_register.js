frappe.query_reports["Employee Asset Register"] = {
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
        },
        {
            fieldname: "assignment_status",
            label: __("Assignment Status"),
            fieldtype: "Select",
            options: "\nActive\nReturned\nCancelled"
        }
    ]
};
