import frappe
import json

def check():
    doctypes = ["Employee Asset Category", "Company Asset", "Asset Request", "Asset Assignment", "Asset Return"]
    results = {}
    for dt in doctypes:
        try:
            doc = frappe.get_meta(dt)
            results[dt] = {
                "istable": doc.istable,
                "issubmittable": doc.is_submittable,
                "module": doc.module,
                "in_create": doc.in_create
            }
        except Exception as e:
            results[dt] = f"Error: {e}"
    print(json.dumps(results, indent=4))

if __name__ == "__main__":
    check()
