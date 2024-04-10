# Copyright (c) 2021, FOSS United and contributors
# For license information, please see license.txt

import json
import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils.telemetry import capture
from lms.lms.utils import get_course_progress
from ...md import find_macros


class CourseLesson(Document):
	def validate(self):
		self.check_and_create_folder()
		self.validate_quiz_id()

	def validate_quiz_id(self):
		if self.quiz_id and not frappe.db.exists("LMS Quiz", self.quiz_id):
			frappe.throw(_("Invalid Quiz ID"))

	def on_update(self):
		dynamic_documents = ["Exercise"]
		for section in dynamic_documents:
			self.update_lesson_name_in_document(section)

	def after_insert(self):
		capture("lesson_created", "lms")

	def update_lesson_name_in_document(self, section):
		doctype_map = {"Exercise": "LMS Exercise", "Quiz": "LMS Quiz"}
		macros = find_macros(self.body)
		documents = [value for name, value in macros if name == section]
		index = 1
		for name in documents:
			e = frappe.get_doc(doctype_map[section], name)
			e.lesson = self.name
			e.index_ = index
			e.course = self.course
			e.save(ignore_permissions=True)
			index += 1
		self.update_orphan_documents(doctype_map[section], documents)

	def update_orphan_documents(self, doctype, documents):
		"""Updates the documents that were previously part of this lesson,
		but not any more.
		"""
		linked_documents = {
			row["name"] for row in frappe.get_all(doctype, {"lesson": self.name})
		}
		active_documents = set(documents)
		orphan_documents = linked_documents - active_documents
		for name in orphan_documents:
			ex = frappe.get_doc(doctype, name)
			ex.lesson = None
			ex.course = None
			ex.index_ = 0
			ex.index_label = ""
			ex.save(ignore_permissions=True)

	def check_and_create_folder(self):
		args = {
			"doctype": "File",
			"is_folder": True,
			"file_name": f"{self.name} {self.course}",
		}
		if not frappe.db.exists(args):
			folder = frappe.get_doc(args)
			folder.save(ignore_permissions=True)

	def get_exercises(self):
		if not self.body:
			return []

		macros = find_macros(self.body)
		exercises = [value for name, value in macros if name == "Exercise"]
		return [frappe.get_doc("LMS Exercise", name) for name in exercises]

	def get_progress(self):
		return frappe.db.get_value(
			"LMS Course Progress", {"lesson": self.name, "owner": frappe.session.user}, "status"
		)

	def get_slugified_class(self):
		if self.get_progress():
			return ("").join([s for s in self.get_progress().lower().split()])
		return


@frappe.whitelist()
def save_progress(lesson, course, status):
	membership = frappe.db.exists(
		"LMS Enrollment", {"member": frappe.session.user, "course": course}
	)
	if not membership:
		return 0
	quiz = frappe.db.get_value("Course Lesson", lesson, "quiz_id")

	if quiz:
		if not frappe.db.exists(
			"LMS Quiz Submission",
			{
				"quiz": quiz,
				"owner": frappe.session.user,
				"catchup": 0,
			},
		):
			return 0
	filters = {"lesson": lesson, "owner": frappe.session.user, "course": course}
	if frappe.db.exists("LMS Course Progress", filters):
		doc = frappe.get_doc("LMS Course Progress", filters)
		doc.status = status
		doc.save(ignore_permissions=True)
	else:
		frappe.get_doc(
			{
				"doctype": "LMS Course Progress",
				"lesson": lesson,
				"status": status,
				"member": frappe.session.user,
			}
		).save(ignore_permissions=True)

	progress = get_course_progress(course)
	
	final_note = -1
	status = False
	x_progress, session_type = frappe.db.get_value("LMS Enrollment", membership, ["progress", "session_type"])
	if progress == 100:
		passing_percentage = frappe.db.get_value("LMS Course", course, "passing_percent")
		if not passing_percentage  or passing_percentage==0:
			passing_percentage = 50
		final_note = get_final_note(course)
		status = "Failed"
		if final_note>= passing_percentage:
			if session_type == "Rattrapage":
				status = "Completed (R)"
			else:
				status = "Completed"

	elif x_progress == 0:
			status = "Started"
	if status:
		set_user_career_course(course, status, final_note)

	frappe.db.set_value("LMS Enrollment", membership, "progress", progress)
	return { "progress": progress, "status": status  }

def get_final_note(course):
	values = {"user_e": frappe.session.user, "course": course}
	data = frappe.db.sql("""select max(qs.creation),qs.quiz, percentage,coefficient from `tabLMS Quiz Submission` qs
join `tabLMS Quiz` q on qs.quiz = q.name
where catchup = 0  and q.in_evaluation = 1 and qs.course = %(course)s and member=%(user_e)s
group by  qs.quiz""", values=values, as_dict=0)
	sum_coef = 0
	sum_note = 0
	for x in data:
		sum_coef  += x[3] 
		sum_note += (x[2] * x[3])
	return sum_note / sum_coef

def set_user_career_course(course, status, final_note):
	career = frappe.get_doc("LMS User Career", {"user_c": frappe.session.user, "status": "Current" })
	user_trainning = frappe.get_doc("LMS User Training", {"parent": career.name, "training": course })
	if final_note > -1:
		user_trainning.note = final_note
	user_trainning.status = status
	user_trainning.save(ignore_permissions=True)


@frappe.whitelist()
def get_lesson_info(chapter):
	return frappe.db.get_value("Course Chapter", chapter, "course")

