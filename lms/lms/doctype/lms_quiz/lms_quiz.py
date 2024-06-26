# Copyright (c) 2021, FOSS United and contributors
# For license information, please see license.txt

import json
import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import cstr, comma_and
from lms.lms.doctype.lms_question.lms_question import validate_correct_answers
from lms.lms.utils import (
	generate_slug,
	has_course_moderator_role,
	has_course_instructor_role,
)


class LMSQuiz(Document):
	def validate(self):
		self.validate_duplicate_questions()
		self.total_marks = set_total_marks(self.name, self.questions)
		self.nbr_question = self.set_nbr_question()

	def set_nbr_question(self):
		nbr_total_qst = len(self.questions)
		nbr_qst = self.nbr_question
		if nbr_qst <= 0:
			return nbr_total_qst
		if nbr_qst > nbr_total_qst:
			return nbr_total_qst
		return nbr_qst
	
	def validate_duplicate_questions(self):
		questions = [row.question for row in self.questions]
		rows = [i + 1 for i, x in enumerate(questions) if questions.count(x) > 1]
		if len(rows):
			frappe.throw(
				_("Rows {0} have the duplicate questions.").format(frappe.bold(comma_and(rows)))
			)

	def on_update(self):
		linked_documents = {
			row["name"] for row in frappe.get_all('Course Lesson', {"quiz_id": self.name})
		}
		for name in linked_documents:
			ex = frappe.get_doc('Course Lesson', name)
			ex.quiz_id = None
			ex.save(ignore_permissions=True)
		e = frappe.get_doc('Course Lesson', self.lesson)
		e.quiz_id = self.name
		e.save(ignore_permissions=True)
	
	def autoname(self):
		if not self.name:
			self.name = generate_slug(self.title, "LMS Quiz")

	def get_last_submission_details(self):
		"""Returns the latest submission for this user."""
		user = frappe.session.user
		if not user or user == "Guest":
			return

		result = frappe.get_all(
			"LMS Quiz Submission",
			fields="*",
			filters={"owner": user, "quiz": self.name},
			order_by="creation desc",
			page_length=1,
		)

		if result:
			return result[0]


def set_total_marks(quiz, questions):
	marks = 0
	for question in questions:
		marks += question.get("marks")
	return marks


@frappe.whitelist()
def quiz_summary(quiz, results):
	course = None
	score = 0
	total_marks = 0
	results = results and json.loads(results)
	for result in results:
		correct = check_answer(result["question"], result["type"], result["answer"])
		
		result["is_correct"] = correct

		question_details = frappe.db.get_value(
			"LMS Quiz Question",
			{"parent": quiz, "idx": result["question_index"]},
			["question", "marks"],
			as_dict=1,
		)
		if result["type"]  ==  "Choices":
			result["is_open"] = 0
		else:
			result["is_open"] = 1
		result["question_name"] = question_details.question
		result["question"] = frappe.db.get_value(
			"LMS Question", question_details.question, "question"
		)
		marks = question_details.marks * correct
		total_marks+= question_details.marks
		result["marks"] = marks
		score += marks

		del result["question_index"]

	quiz_details = frappe.db.get_value(
		"LMS Quiz", quiz, ["passing_percentage"], as_dict=1
	)
	percentage = (score / total_marks) * 100

	submission = frappe.get_doc(
		{
			"doctype": "LMS Quiz Submission",
			"quiz": quiz,
			"result": results,
			"course": course,
			"score": score,
			"score_out_of": total_marks,
			"member": frappe.session.user,
			"percentage": percentage,
			"passing_percentage": quiz_details.passing_percentage,
		}
	)
	submission.save(ignore_permissions=True)

	return {
		"score": score,
		"score_out_of": total_marks,
		"submission": submission.name,
		"pass": percentage >= quiz_details.passing_percentage,
		"percentage": percentage,
	}


@frappe.whitelist()
def save_quiz(
	quiz_title,
	passing_percentage,
	questions,
	max_attempts=0,
	quiz=None,
	show_answers=1,
	show_submission_history=0,
):
	if not has_course_moderator_role() or not has_course_instructor_role():
		return
	
	values = {
		"title": quiz_title,
		"passing_percentage": passing_percentage,
		"max_attempts": max_attempts,
		"show_answers": show_answers,
		"show_submission_history": show_submission_history,
	}

	if quiz:
		frappe.db.set_value("LMS Quiz", quiz, values)
		update_questions(quiz, questions)
		return quiz
	else:
		doc = frappe.new_doc("LMS Quiz")
		doc.update(values)
		doc.save()
		update_questions(doc.name, questions)
		return doc.name


def update_questions(quiz, questions):
	questions = json.loads(questions)

	delete_questions(quiz, questions)
	add_questions(quiz, questions)
	frappe.db.set_value("LMS Quiz", quiz, "total_marks", set_total_marks(quiz, questions))


def delete_questions(quiz, questions):
	existing_questions = frappe.get_all(
		"LMS Quiz Question",
		{
			"parent": quiz,
		},
		pluck="name",
	)

	current_questions = [question.get("question_name") for question in questions]

	for question in existing_questions:
		if question not in current_questions:
			frappe.db.delete("LMS Quiz Question", question)


def add_questions(quiz, questions):
	for index, question in enumerate(questions):
		question = frappe._dict(question)
		if question.question_name:
			doc = frappe.get_doc("LMS Quiz Question", question.question_name)
		else:
			doc = frappe.new_doc("LMS Quiz Question")
			doc.update(
				{
					"parent": quiz,
					"parenttype": "LMS Quiz",
					"parentfield": "questions",
					"idx": index + 1,
				}
			)

		doc.update({"question": question.question, "marks": question.marks})

		doc.save()


@frappe.whitelist()
def save_question(quiz, values, index):
	values = frappe._dict(json.loads(values))

	if values.get("name"):
		doc = frappe.get_doc("LMS Question", values.get("name"))
	else:
		doc = frappe.new_doc("LMS Question")

	doc.update(
		{
			"question": values.question,
			"type": values["type"],
		}
	)

	for num in range(1, 5):
		if values.get(f"option_{num}"):
			doc.update(
				{
					f"option_{num}": values[f"option_{num}"],
					f"is_correct_{num}": values[f"is_correct_{num}"],
				}
			)

		if values.get(f"explanation_{num}"):
			doc.update(
				{
					f"explanation_{num}": values[f"explanation_{num}"],
				}
			)

		if values.get(f"possibility_{num}"):
			doc.update(
				{
					f"possibility_{num}": values[f"possibility_{num}"],
				}
			)

	doc.save()
	return doc.name


@frappe.whitelist()
def get_question_details(question):
	if frappe.db.exists("LMS Quiz Question", question):
		fields = ["name", "question", "type"]
		for num in range(1, 7):
			fields.append(f"option_{cstr(num)}")
			fields.append(f"is_correct_{cstr(num)}")
			fields.append(f"explanation_{cstr(num)}")
			fields.append(f"possibility_{cstr(num)}")

		return frappe.db.get_value("LMS Quiz Question", question, fields, as_dict=1)
	return


@frappe.whitelist()
def check_answer(question, type, answers):
	#answers = json.loads(answers)
	if type == "Choices":
		return check_choice_answers(question, answers)
	else:
		return check_input_answers(question, answers[0])


def check_choice_answers(question, answers):
	fields = []
	correct = 0
	incorrect = 0
	an_correct = 0
	for num in range(1, 7):
		fields.append(f"option_{cstr(num)}")
		fields.append(f"is_correct_{cstr(num)}")

	question_details = frappe.db.get_value("LMS Question", question, fields, as_dict=1)
	for num in range(1, 7):
		if question_details[f"is_correct_{num}"]:
			an_correct += 1
			if question_details[f"option_{num}"] in answers:
				correct += 1
			#else:
			#	incorrect += 1
		elif question_details[f"option_{num}"] and question_details[f"option_{num}"] in answers:
			incorrect += 1
	point = (correct - incorrect) / (an_correct if an_correct != 0 else 1)
	return point if point > 0 else 0


def check_input_answers(question, answer):
	fields = []
	for num in range(1, 5):
		fields.append(f"possibility_{cstr(num)}")

	question_details = frappe.db.get_value("LMS Question", question, fields, as_dict=1)
	for num in range(1, 5):
		current_possibility = question_details[f"possibility_{num}"]
		if current_possibility and current_possibility.lower() == answer.lower():
			return 1

	return 0


@frappe.whitelist()
def get_user_quizzes():
	filters = {} if has_course_moderator_role() else {"owner": frappe.session.user}
	return frappe.get_all("LMS Quiz", filters=filters, fields=["name", "title"])
