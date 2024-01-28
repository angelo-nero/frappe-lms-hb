import frappe
from frappe import _
from lms.overrides.user import get_enrolled_courses

def get_context(context):
    context.no_cache = 1
    if frappe.session.user == "Guest":
	    raise frappe.PermissionError(_("You don't have permission to access this page."))        
    username = frappe.db.get_value("User", frappe.session.user, ["username"])

    context.member = frappe.get_doc("User", {"username": username})

    values = {"user_e": context.member.email}
    
    data = frappe.db.sql("""SELECT 'Commencées', count(*),'Started'
FROM `tabLMS User Training` lut
JOIN `tabLMS User Career` luc ON luc.name = lut.parent
WHERE luc.user_c = %(user_e)s and lut.status = 'Started' UNION
                         SELECT 'Terminées', count(*),'Completed'
FROM `tabLMS User Training` lut
JOIN `tabLMS User Career` luc ON luc.name = lut.parent
WHERE luc.user_c = %(user_e)s and lut.status = 'Completed' UNION
                         SELECT 'Échouées', count(*),'Failed'
FROM `tabLMS User Training` lut
JOIN `tabLMS User Career` luc ON luc.name = lut.parent
WHERE luc.user_c = %(user_e)s and lut.status = 'Failed'""", values=values, as_dict=0)
    
    context.recap_data = data