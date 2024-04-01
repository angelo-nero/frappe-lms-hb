# Copyright (c) 2024, Frappe and contributors
# For license information, please see license.txt

# import frappe
import json
import random
import frappe
from frappe.model.document import Document
from frappe import _

class LMSClass(Document):
	pass

@frappe.whitelist()
def end_session(doc):
	class_data = json.loads(doc)
	doc = frappe.get_doc("LMS Class", class_data['name'])
	if doc.is_closed:
		frappe.msgprint(_('Session is closed'))
	else:
		for item_stud in class_data['students']:
			for item_train in class_data['training']:
				filter_criteria = {"status": "Current", "user_c": item_stud['student']}
				doc_uc = frappe.get_all("LMS User Career", filters=filter_criteria, limit=1)            
				for x in doc_uc:                
					filter_criteria = {"status": "Not started", "parent": x.name, "training": item_train['training']}                
					if frappe.db.exists("LMS User Training", filter_criteria):                    
						doc_ut = frappe.get_last_doc("LMS User Training", filters=filter_criteria)
						doc_ut.status = 'Started'
						filter_criteria = {"member_type": "Student", "role": "Member", "course":  item_train['training'], "member": item_stud['student']}
						if not frappe.db.exists("LMS Enrollment", filter_criteria):                       
							doc_enrol = frappe.new_doc("LMS Enrollment")                        
							doc_enrol.member_type = "Student"                        
							doc_enrol.role = "Member"                        
							doc_enrol.course = item_train['training']                       
							doc_enrol.member = item_stud['student']                        
							doc_enrol.save()
							doc_ut.save()                
					else:
						frappe.msgprint(_('User Training is not equal a NOT-STARTED'))
		doc.is_closed = True
		doc.save()
		frappe.msgprint(_('Class ended. !'))

