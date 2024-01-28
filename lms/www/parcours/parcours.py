import datetime
import json
import frappe
from frappe import _
from lms.overrides.user import get_enrolled_courses

def get_context(context):
    context.no_cache = 1
    if frappe.session.user == "Guest":
	    raise frappe.PermissionError(_("You don't have permission to access this page."))
    
    tab = 'dashboard'
    
    try:
        tab = switch(frappe.form_dict["xsaoaz"])
    except KeyError:
        tab = 'parcours'
        

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

    if tab == 'parcours':
        data = frappe.db.sql("""
                                SELECT
                                lut.idx,luc.career,module,lt.title,lut.status,lcti.is_open,lt.title,lcti.is_classroom,start_date,lt.categorie,lmd.parent_lms_module as parent_module
                             ,lt.name   
                             FROM `tabLMS User Career` luc
                                join `tabLMS User Training` lut on luc.name = lut.parent
                                join `tabLMS Career Training` lct on luc.career = lct.career
                                join `tabLMS Module`lmd on lmd.name = lct.module
                                join `tabLMS Training` lcti on lct.name = lcti.parent and lcti.course = lut.training
                                join `tabLMS Course` lt on lut.training = lt.name
                                left join (select start_date, student, training
                                                    from `tabLMS Class` cl
                                                            join `tabLMS Class Training` ti on cl.name = ti.parent
                                                            join `tabLMS Class Student` cs on cl.name = cs.parent
                                                    where student = %(user_e)s  and end_date >= now() and is_closed = 0) as cst
                                                on luc.user_c = cst.student and lut.training = cst.training
                                where luc.status = 'Current' and luc.user_c = %(user_e)s
                                order by lut.idx;
                                """, values=values, as_dict=0)
        res_dict = {}
        module_dict = {}
        title = ''
        for x in data:
            title = x[1]
            if x[10] == '' or x[10] == None:   
                if x[2]  not  in module_dict:
                    module_dict[x[2]] = 0
            else:
                if x[10] not  in module_dict:
                    module_dict[x[10]] = []
                if x[2] not  in module_dict[x[10]]:
                    module_dict[x[10]].append(x[2])
            
            if x[2] not in res_dict:
                res_dict[x[2]] = []
            res_dict[x[2]].append({"training" : x[3], "status": x[4] if x[4] != 'Not started' else 'not-started', "is_open": x[5], "course": x[11]
            , "is_classroom": x[7],"start_date":x[8], "tag":x[9],"classroom": 'CLUB' if x[7] else 'E-Learning'
                
            })
        context.title_ = title
        context.tab_parcours = module_dict
        context.parcours = res_dict
    elif tab == 'dashboard':
        data = frappe.db.sql("""
                                SELECT course,progress,lut.status
                                FROM `tabLMS User Career` luc
                                        join `tabLMS User Training` lut on luc.name = lut.parent and luc.user_c = %(user_e)s
                                        left join `tabLMS Enrollment` lbm on luc.user_c = lbm.member and lut.training = lbm.course
                                where lbm.member = %(user_e)s
                                order by progress desc;
                                """, values=values, as_dict=0)
        res_dict = []
        not_started = 0
        started = 0
        failed = 0
        completed = 0
        for x in data:
            if x[2] =='Not started':
                not_started = not_started +1
            elif x[2] =='Started':
                started = started +1
            elif x[2] =='Completed':
                completed = completed +1
            elif x[2] =='Failed':
                failed = failed +1
            class_prog = ''
            if x[1] <= 30:
                class_prog = 'pro-red'
            elif x[1]>30 and x[1] <= 60:
                class_prog = 'pro-orange'
            elif x[1]>60 and x[1] <= 99:
                class_prog = 'pro-blue'
            else:
                class_prog = 'pro-green'
            res_dict.append({"course": x[0], "status": x[2], "progress": x[1], "class_prog":class_prog})
        context.dashbord = res_dict
        context.not_started = not_started
        context.started = started
        context.failed = failed
        context.completed = completed


        courses_continued= []
        courses_subscribed = []
        filters = {"member": context.member.email, "member_type": 'Student'}
        memberships = frappe.get_all("LMS Enrollment", filters, ["name", "course", "progress"])
        for membership in memberships:
            course = frappe.db.get_value(
                "LMS Course",
                membership.course,
                [
                    "name",
                    "upcoming",
                    "title",
                    "short_introduction",
                    "image",
                    "enable_certification",
                    "currency",
                    "published",
                ],
                as_dict=True,
            )
            if not course.published:
                continue
            if membership.progress > 0:
                courses_continued.append(course)
            else:
                courses_subscribed.append(course)
        context.courses_continued = courses_continued
        context.courses_subscribed = courses_subscribed
    elif tab == 'courses':
        courses = []
        filters = {"member": context.member.email, "member_type": 'Student'}
        memberships = frappe.get_all("LMS Enrollment", filters, ["name", "course", "progress"])
        for membership in memberships:
            course = frappe.db.get_value(
                "LMS Course",
                membership.course,
                [
                    "name",
                    "upcoming",
                    "title",
                    "short_introduction",
                    "image",
                    "enable_certification",
                    "currency",
                    "published",
                ],
                as_dict=True,
            )
            if not course.published:
                continue
            courses.append(course)
        context.enrolled_courses = courses
    elif tab == 'biblio':
        bibliotheque = frappe.get_all("LMS Bibliotheques", fields=["label", "img", "name"],  order_by="order_show")
        context.biblio  =  bibliotheque
    elif tab == 'biblio-dtl':
        biblio_dtl = frappe.get_doc("LMS Bibliotheques", frappe.form_dict["idx"]).as_dict()
        context.biblio_dtl_txt = biblio_dtl["label"]
        res = {key: filter(biblio_dtl[key]) for key in biblio_dtl.keys()
        & {"stage_report","inter_pub","technic_doc"}}
        context.biblio_dtl_txt = biblio_dtl["label"]
        context.biblio_dtl  = res
    context.tab = tab
 
def filter(data):
    res = []
    for x in data:
        res.append({key: x[key] for key in x.keys()
        & {"label","file","type "}})
    return res

def switch(tab):
    if tab == "oadazk":
        return "dashboard"
    elif tab == "feasqda":
        return "courses"
    elif tab == "aozdlaz":
        return "quiz"
    elif tab == "Solidity":
        return "biblio"
    elif  tab == 'dtl-ytidilos':
        return "biblio-dtl"
    else:
        return "parcours"