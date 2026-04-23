frappe.query_reports["Asset History by Device"] = {
    filters: [
        {
            fieldname: "company_asset",
            label: __("Company Asset"),
            fieldtype: "Link",
            options: "Company Asset"
        }
    ]
};
