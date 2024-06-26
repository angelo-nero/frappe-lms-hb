import frappe
from frappe import _
from frappe.utils import cstr, flt
from lms.lms.md import markdown_to_html

from lms.lms.utils import (
	get_lesson_url,
	get_progress,
	has_course_moderator_role,
	is_instructor,
	has_course_evaluator_role,
)
from lms.www.utils import (
	get_common_context,
	get_last_lesson_is_completed,
	redirect_to_lesson,
	get_current_lesson_details,
)


def get_context(context):
	get_common_context(context)

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

	chapter_index = frappe.form_dict.get("chapter")
	lesson_index = frappe.form_dict.get("lesson")
	class_name = frappe.form_dict.get("class")

	if class_name:
		context.class_info = frappe._dict(
			{
				"name": class_name,
				"title": frappe.db.get_value("LMS Batch", class_name, "title"),
			}
		)

	lesson_number = f"{chapter_index}.{lesson_index}"
	context.lesson_number = lesson_number
	context.lesson_index = lesson_index
	context.chapter = frappe.db.get_value(
		"Chapter Reference", {"idx": chapter_index, "parent": context.course.name}, "chapter"
	)

	if not chapter_index or not lesson_index:
		index_ = "1.1"
		redirect_to_lesson(context.course, index_)

	context.lesson = get_current_lesson_details(lesson_number, context)
	context.instructor = is_instructor(context.course.name)
	context.is_moderator = has_course_moderator_role()
	context.is_evaluator = has_course_evaluator_role()

	if context.lesson.instructor_notes:
		context.instructor_notes = markdown_to_html(context.lesson.instructor_notes)

	context.show_lesson = (
		context.membership
		or (context.lesson and context.lesson.include_in_preview)
		or context.instructor
		or context.is_moderator
		or context.is_evaluator
	)

	if not context.lesson:
		context.lesson = frappe._dict()

	if frappe.form_dict.get("edit"):
		if not context.instructor and not context.is_moderator:
			raise frappe.PermissionError(_("You do not have permission to access this page."))
		context.lesson.edit_mode = True
	else:
		neighbours = get_neighbours(lesson_number, context.lessons)
		context.next_id = neighbours["next"]
		if context.lesson.quiz_id == None or context.lesson.quiz_id == '' or get_progress(context.course.name, context.lesson.name)  == 'Complete':
			context.next_url = get_url(neighbours["next"], context.course)
		context.prev_url = get_url(neighbours["prev"], context.course)
		if neighbours["prev"] and context.lesson.depend_to:
			if not get_last_lesson_is_completed(neighbours["prev"],  context):
				context.lesson.body = '<div style="padding: 1.8rem 0;text-align: center;font-size: x-large;color: red;">Vous devez terminer la séquence précédente !</div>'
				context.lesson.youtube = ""
				context.lesson.quiz_id  =  ""
				context.next_url = ""
			elif not neighbours["next"]:
				context.next_id = "endAndCert"
		elif not neighbours["prev"] and not neighbours["next"]:
			context.next_id = "endAndCert" 
			

	meta_info = (
		context.lesson.title + " - " + context.course.title
		if context.lesson.title
		else "New Lesson"
	)
	context.metatags = {
		"title": meta_info,
		"keywords": meta_info,
		"description": meta_info,
	}

	context.page_extensions = get_page_extensions(context)
	context.page_context = {
		"course": context.course.name,
		"batch_old": context.batch_old,
		"lesson": context.lesson.name if context.lesson.name else "New Lesson",
		"is_member": context.membership is not None,
	}


def get_url(lesson_number, course):
	return (
		get_lesson_url(course.name, lesson_number)
		and get_lesson_url(course.name, lesson_number) + course.query_parameter
	)


def get_page_extensions(context):
	default_value = ["lms.plugins.PageExtension"]
	classnames = frappe.get_hooks("lms_lesson_page_extensions") or default_value
	extensions = [frappe.get_attr(name)() for name in classnames]
	for e in extensions:
		e.set_context(context)
	return extensions


def get_neighbours(current, lessons):
	numbers = [lesson.number for lesson in lessons]
	tuples_list = [tuple(int(x) for x in s.split(".")) for s in numbers]
	sorted_tuples = sorted(tuples_list)
	sorted_numbers = [".".join(str(num) for num in t) for t in sorted_tuples]
	index = sorted_numbers.index(current)

	return {
		"prev": sorted_numbers[index - 1] if index - 1 >= 0 else None,
		"next": sorted_numbers[index + 1] if index + 1 < len(sorted_numbers) else None,
	}
