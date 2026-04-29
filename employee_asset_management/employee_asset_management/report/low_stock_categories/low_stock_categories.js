frappe.query_reports["Low Stock Categories"] = {
    filters: [
        {
            fieldname: "asset_category",
            label: __("Employee Asset Category"),
            fieldtype: "Link",
            options: "Employee Asset Category"
        },
        {
            fieldname: "show_all_threshold_categories",
            label: __("Show All Threshold Categories"),
            fieldtype: "Check",
            default: 0
        }
    ]
};
