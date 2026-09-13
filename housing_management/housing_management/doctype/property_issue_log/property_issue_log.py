# Copyright (c) 2026, pluto and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document

class PropertyIssueLog(Document):
    def on_update(self):
        self.auto_create_expense_log()

    def auto_create_expense_log(self):
        status = getattr(self, "status", None)
        cost = float(getattr(self, "repair_cost", 0) or 0)
        prop = getattr(self, "housing_property", None) or getattr(self, "property", None)

        if status in ["Resolved", "Closed"] and cost > 0 and prop:
            identifier = f"Issue Log: {self.name}"
            
            # Check for existing expense entries safely
            has_desc = frappe.db.has_column("Property Expense Log", "description")
            existing = False
            if has_desc:
                existing = frappe.db.sql("""
                    SELECT name FROM `tabProperty Expense Log`
                    WHERE description LIKE %s
                """, (f"%{identifier}%",))

            if not existing:
                expense_data = {
                    "doctype": "Property Expense Log",
                    "amount": cost,
                    "description": f"Auto-generated from {identifier} - {getattr(self, 'description', '') or 'Maintenance Repair'}"
                }

                if frappe.db.has_column("Property Expense Log", "housing_property"):
                    expense_data["housing_property"] = prop
                if frappe.db.has_column("Property Expense Log", "property"):
                    expense_data["property"] = prop

                expense = frappe.get_doc(expense_data)
                expense.insert(ignore_permissions=True)
                frappe.msgprint(_("Auto-created Property Expense Log for repair cost of ${0}").format(cost))
