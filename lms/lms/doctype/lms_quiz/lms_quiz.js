// Copyright (c) 2021, FOSS United and contributors
// For license information, please see license.txt

frappe.ui.form.on("LMS Quiz", {
	refresh: function (frm) {
	}
});

frappe.ui.form.on("LMS Quiz", "course", function (frm) {
	frm.set_query("lesson", function () {
		return {
			"filters": {
				"course": frm.doc.course
			}
		};
	});
});

frappe.ui.form.on("LMS Quiz Question", {
	marks: function (frm) {
		total_marks = 0;
		frm.doc.questions.forEach((question) => {
			total_marks += question.marks;
		});
		frm.doc.total_marks = total_marks;
	},
});
