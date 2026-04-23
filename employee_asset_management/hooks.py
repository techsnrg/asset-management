app_name = "employee_asset_management"
app_title = "Employee Asset Management"
app_publisher = "Somil Vaishya"
app_description = "Asset Management System"
app_email = "admin@example.com"
app_license = "mit"

after_install = "employee_asset_management.setup.run_setup"

scheduler_events = {
    "daily": [
        "employee_asset_management.employee_asset_management.tasks.send_due_reminders",
    ]
}

doctype_js = {
    "Delivery Note": "public/js/delivery_note.js",
}

permission_query_conditions = {
    "Asset Request": "employee_asset_management.employee_asset_management.permissions.asset_request_query",
    "Asset Assignment": "employee_asset_management.employee_asset_management.permissions.asset_assignment_query",
    "Asset Return": "employee_asset_management.employee_asset_management.permissions.asset_return_query",
    "Company Asset": "employee_asset_management.employee_asset_management.permissions.company_asset_query",
    "Employee Sample Issue": "employee_asset_management.employee_asset_management.permissions.employee_sample_issue_query",
}

has_permission = {
    "Asset Request": "employee_asset_management.employee_asset_management.permissions.asset_request_has_permission",
    "Asset Assignment": "employee_asset_management.employee_asset_management.permissions.asset_assignment_has_permission",
    "Asset Return": "employee_asset_management.employee_asset_management.permissions.asset_return_has_permission",
    "Company Asset": "employee_asset_management.employee_asset_management.permissions.company_asset_has_permission",
    "Employee Sample Issue": "employee_asset_management.employee_asset_management.permissions.employee_sample_issue_has_permission",
}

fixtures = [
    {"dt": "Asset Management Settings"},
    {"dt": "Allowed On Behalf Requester Role"},
    {"dt": "Asset Category"},
    {"dt": "Asset Category Issuer Role"},
    {"dt": "Company Asset"},
    {"dt": "Asset Request"},
    {"dt": "Asset Assignment"},
    {"dt": "Asset Return"},
    {"dt": "Number Card"},
    {"dt": "Dashboard Chart"},
    {"dt": "Report"},
    {"dt": "Workspace"},
]
