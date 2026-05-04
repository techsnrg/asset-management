import re

import frappe
from frappe.model.naming import make_autoname
from frappe.model.rename_doc import rename_doc


DOCTYPE_SERIES = {
    "Asset Request": ("ARQ-.YYYY.-.#####", re.compile(r"^ARQ-\d{4}-\d{5}(?:-\d+)?$")),
    "Asset Assignment": ("ASN-.YYYY.-.#####", re.compile(r"^ASN-\d{4}-\d{5}(?:-\d+)?$")),
    "Asset Return": ("ART-.YYYY.-.#####", re.compile(r"^ART-\d{4}-\d{5}(?:-\d+)?$")),
    "Employee Sample Issue": ("ESI-.YYYY.-.#####", re.compile(r"^ESI-\d{4}-\d{5}(?:-\d+)?$")),
}


def execute():
    for doctype, (series, pattern) in DOCTYPE_SERIES.items():
        if not frappe.db.exists("DocType", doctype):
            continue

        for name in frappe.get_all(doctype, pluck="name"):
            if pattern.match(name):
                continue

            new_name = make_autoname(series)
            rename_doc(doctype, name, new_name, force=True, merge=False)
