import frappe
from frappe.model.document import Document

class HousingAssignment(Document):
    def on_submit(self):
        # 1. Update the bed in the Apartment to Occupied
        self.update_bed_status("Occupied", self.employee)
        # 2. Automatically set the housing fields on the HR Employee profile
        self.update_employee_profile(self.apartment, self.bed_id, self.check_in_date)

    def on_cancel(self):
        # 1. Revert the bed back to Vacant
        self.update_bed_status("Vacant", None)
        # 2. Clear the housing fields on the HR Employee profile
        self.update_employee_profile(None, None, None)

    def update_bed_status(self, status, tenant):
        if not self.apartment or not self.bed_id:
            return
            
        apartment = frappe.get_doc("Apartment", self.apartment)
        for bed in apartment.beds:
            if bed.bed_id == self.bed_id:
                bed.status = status
                bed.current_tenant = tenant
        apartment.save(ignore_permissions=True)

    def update_employee_profile(self, apartment, bed, date):
        if not self.employee:
            return
            
        frappe.db.set_value("Employee", self.employee, {
            "custom_current_apartment": apartment,
            "custom_current_bed": bed,
            "custom_move_in_date": date
        })