# Copyright (c) 2026, pluto and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document

class TenantAssignment(Document):
    def validate(self):
        status = getattr(self, "assignment_status", None) or getattr(self, "status", None)
        if status != "Active":
            return

        emp = getattr(self, "foreign_employee_name", None) or getattr(self, "employee_name", None)
        prop = getattr(self, "housing_property", None) or getattr(self, "property", None)

        if emp:
            existing = frappe.db.sql("""
                SELECT name FROM `tabTenant Assignment`
                WHERE (foreign_employee_name = %s OR employee_name = %s)
                  AND (assignment_status = 'Active' OR status = 'Active')
                  AND name != %s
            """, (emp, emp, self.name or ''))
            if existing:
                frappe.throw(_("This employee is already actively assigned to a property. End their current assignment first."))

        if prop:
            total_beds = frappe.db.get_value("Housing Property", prop, "total_beds") or frappe.db.get_value("Housing Property", prop, "max_capacity") or 1
            current_occ = frappe.db.sql("""
                SELECT COUNT(*) FROM `tabTenant Assignment`
                WHERE (housing_property = %s OR property = %s)
                  AND (assignment_status = 'Active' OR status = 'Active')
                  AND name != %s
            """, (prop, prop, self.name or ''))[0][0] or 0

            if current_occ >= total_beds:
                frappe.throw(_("Cannot assign employee. Property '{0}' is at its maximum capacity of {1} beds.").format(prop, total_beds))
