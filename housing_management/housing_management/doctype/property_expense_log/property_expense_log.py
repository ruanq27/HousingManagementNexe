# Copyright (c) 2026, pluto and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class PropertyExpenseLog(Document):
    def on_update(self):
        self.update_property_total_expenses()

    def on_trash(self):
        self.update_property_total_expenses()

    def update_property_total_expenses(self):
        prop = getattr(self, "housing_property", None) or getattr(self, "property", None)
        if not prop:
            return

        col = "housing_property" if frappe.db.has_column("Property Expense Log", "housing_property") else "property"

        total = frappe.db.sql(f"""
            SELECT SUM(amount)
            FROM `tabProperty Expense Log`
            WHERE `{col}` = %s
        """, (prop,))[0][0] or 0.0

        frappe.db.set_value("Housing Property", prop, "total_expenses", total)
