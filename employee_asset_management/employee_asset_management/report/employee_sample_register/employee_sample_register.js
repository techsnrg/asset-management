frappe.query_reports["Employee Sample Register"] = {
    filters: [
        {
            fieldname: "employee",
            label: __("Employee"),
            fieldtype: "Link",
            options: "Employee"
        },
        {
            fieldname: "status",
            label: __("Status"),
            fieldtype: "Select",
            options: "\nOpen\nPartially Returned\nClosed"
        }
    ]
};
