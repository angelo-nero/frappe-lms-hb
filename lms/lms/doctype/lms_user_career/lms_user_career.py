# Copyright (c) 2024, Frappe and contributors
# For license information, please see license.txt

# import frappe
import frappe
from frappe.model.document import Document
from frappe import _

class LMSUserCareer(Document):
	
	def before_insert(self):
		values = {"career": self.career}
		data = frappe.db.sql("SELECT lcti.course,lcti.is_open from `tabLMS Career Training` lct join `tabLMS Training` lcti on lct.name = lcti.parent where career=%(career)s order by order_t_c, lcti.idx;", values=values, as_dict=0)    
		for x in data:
			self.append('training', {
				'training': x[0],
				'can_read': x[1],
				'status': 'Not started'
			})
			if x[1] == 1:
				try:
					doc_enrol = frappe.new_doc("LMS Enrollment")        
					doc_enrol.member_type = "Student"        
					doc_enrol.role = "Member"
					doc_enrol.course = x[0]
					doc_enrol.member = self.user_c
					doc_enrol.save()
				except Exception as e:
					print(e)

	def after_insert(self):
		frappe.db.sql("UPDATE `tabLMS User Career` set status = 'Terminé' where user_c = %(user_c)s and name <> %(name)s;", values={"user_c": self.user_c, "name": self.name}, as_dict=0)    

	def on_update(self):
		if self.status == 'Current':
			frappe.db.sql("UPDATE `tabLMS User Career` set status = 'Terminé' where user_c = %(user_c)s and name <> %(name)s;", values={"user_c": self.user_c, "name": self.name}, as_dict=0)    

