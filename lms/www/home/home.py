import datetime
import json
import frappe
from frappe import _


def get_context(context):
    context.no_cache = 1

    data = getData()
    context.free_session_url = data["free_session_url"]
    context.years_of_experience = data["years_of_experience"]
    context.satisfied_parents = data["satisfied_parents"]
    context.islamic_courses = data["islamic_courses"]
    context.dedicated_teachers = data["dedicated_teachers"]
    context.tilmid_pack_price = data["tilmid_pack_price"]
    context.talib_pack_price = data["talib_pack_price"]
    context.mojtahid_pack_price = data["mojtahid_pack_price"]
    context.tilmid_pack_url = data["tilmid_pack_url"]
    context.talib_pack_url= data["talib_pack_url"]
    context.mojtahid_pack_url = data["mojtahid_pack_url"]
    context.video_discover_values = data["video_discover_values"]
    context.video_why_chosing = data["video_why_chosing"]

@frappe.whitelist(allow_guest=True)
def getData():
    return frappe.get_all(
		"LMS Home data",
        filters={"name":"HOME"},
		fields=["*"],
	)[0]