import datetime
import json
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
    
    data = frappe.db.sql("""
                                SELECT lut.status,count(*)
                                FROM `tabLMS User Career` luc
                                        join `tabLMS User Training` lut on luc.name = lut.parent and luc.user_c = %(user_e)s
                                        left join `tabLMS Enrollment` lbm on luc.user_c = lbm.member and lut.training = lbm.course
                                where lut.status <> 'Not started' and lbm.member = %(user_e)s
                         group by lut.status      
                         order by lut.status;
                                """, values=values, as_dict=0)
    
    context.recap_data = data