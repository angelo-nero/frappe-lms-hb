frappe.ready(() => {
	$(".menu-main > li").click((e) => {
		if (e.currentTarget.attributes['data-link'].value == 'forum')
			document.location.href = '/forum'
		else
			document.location.href = '/parcours?xsaoaz=' + e.currentTarget.attributes['data-link'].value
	});
	hide_wrapped_mentor_cards();

	$(".review-link").click((e) => {
		show_review_dialog(e);
	});

	$(".icon-rating").click((e) => {
		highlight_rating(e);
	});

	$("#submit-review").click((e) => {
		submit_review(e);
	});
	if (hasUrlParam("end") && $('.final_result > .icons  > .final-stat').attr("href") && $('.final_result > .icons  > .final-stat').attr("href") == "#icon-completed")
		celebrate();
	$("#certification").click((e) => {
		create_certificate(e);
	});

	$("#submit-for-review").click((e) => {
		submit_for_review(e);
	});
});

const hasUrlParam = (paramName) => {
	const queryString = window.location.search;
	const urlParams = new URLSearchParams(queryString);
	return urlParams.has(paramName);
}

const hide_wrapped_mentor_cards = () => {
	let offset_top_prev;

	$(".member-parent .member-card").each(function () {
		var offset_top = $(this).offset().top;
		if (offset_top > offset_top_prev) {
			$(this).addClass("wrapped").slideUp("fast");
		}
		if (!offset_top_prev) {
			offset_top_prev = offset_top;
		}
	});

	if ($(".wrapped").length < 1) {
		$(".view-all-mentors").hide();
	}
};

const show_review_dialog = (e) => {
	e.preventDefault();
	$("#review-modal").modal("show");
};

const highlight_rating = (e) => {
	var rating = $(e.currentTarget).attr("data-rating");
	$(".icon-rating").removeClass("star-click");
	$(".icon-rating").each((i, elem) => {
		if (i <= rating - 1) {
			$(elem).addClass("star-click");
		}
	});
};

const submit_review = (e) => {
	e.preventDefault();
	let rating = $(".rating-field").children(".star-click").length;
	let review = $(".review-field").val();
	if (!rating) {
		$(".error-field").text("Please provide a rating.");
		return;
	}
	frappe.call({
		method: "lms.lms.doctype.lms_course_review.lms_course_review.submit_review",
		args: {
			rating: rating,
			review: review,
			course: decodeURIComponent($(e.currentTarget).attr("data-course")),
		},
		callback: (data) => {
			if (data.message == "OK") {
				$(".review-modal").modal("hide");
				frappe.show_alert(
					{
						message: __("Review submitted."),
						indicator: "green",
					},
					3
				);
				setTimeout(() => {
					window.location.reload();
				}, 1000);
			}
		},
	});
};

const create_certificate = (e) => {
	e.preventDefault();
	course = $(e.currentTarget).attr("data-course");
	frappe.call({
		method: "lms.lms.doctype.lms_certificate.lms_certificate.create_certificate",
		args: {
			course: course,
		},
		callback: (data) => {
			window.location.href = `/courses/${course}/${data.message.name}`;
		},
	});
};

const element_not_in_viewport = (el) => {
	const rect = el.getBoundingClientRect();
	return (
		rect.bottom < 0 ||
		rect.right < 0 ||
		rect.left > window.innerWidth ||
		rect.top > window.innerHeight
	);
};

const submit_for_review = (e) => {
	let course = $(e.currentTarget).data("course");
	frappe.call({
		method: "lms.lms.doctype.lms_course.lms_course.submit_for_review",
		args: {
			course: course,
		},
		callback: (data) => {
			if (data.message == "No Chp") {
				frappe.msgprint(
					__(`There are no chapters in this course.
                Please add chapters and lessons to your course before you submit it for review.`)
				);
			} else if (data.message == "OK") {
				frappe.show_alert(
					{
						message: __(
							"Your course has been submitted for review."
						),
						indicator: "green",
					},
					3
				);
				setTimeout(() => {
					window.location.reload();
				}, 1000);
			}
		},
	});
};


const celebrate = () => {
	// Globals
	var random = Math.random
		, cos = Math.cos
		, sin = Math.sin
		, PI = Math.PI
		, PI2 = PI * 2
		, timer = undefined
		, frame = undefined
		, confetti = [];

	var particles = 10
		, spread = 40
		, sizeMin = 3
		, sizeMax = 12 - sizeMin
		, eccentricity = 10
		, deviation = 100
		, dxThetaMin = -.1
		, dxThetaMax = -dxThetaMin - dxThetaMin
		, dyMin = .13
		, dyMax = .18
		, dThetaMin = .4
		, dThetaMax = .7 - dThetaMin;

	var colorThemes = [
		function () {
			return color(200 * random() | 0, 200 * random() | 0, 200 * random() | 0);
		}, function () {
			var black = 200 * random() | 0; return color(200, black, black);
		}, function () {
			var black = 200 * random() | 0; return color(black, 200, black);
		}, function () {
			var black = 200 * random() | 0; return color(black, black, 200);
		}, function () {
			return color(200, 100, 200 * random() | 0);
		}, function () {
			return color(200 * random() | 0, 200, 200);
		}, function () {
			var black = 256 * random() | 0; return color(black, black, black);
		}, function () {
			return colorThemes[random() < .5 ? 1 : 2]();
		}, function () {
			return colorThemes[random() < .5 ? 3 : 5]();
		}, function () {
			return colorThemes[random() < .5 ? 2 : 4]();
		}
	];
	function color(r, g, b) {
		return 'rgb(' + r + ',' + g + ',' + b + ')';
	}

	// Cosine interpolation
	function interpolation(a, b, t) {
		return (1 - cos(PI * t)) / 2 * (b - a) + a;
	}

	// Create a 1D Maximal Poisson Disc over [0, 1]
	var radius = 1 / eccentricity, radius2 = radius + radius;
	function createPoisson() {
		// domain is the set of points which are still available to pick from
		// D = union{ [d_i, d_i+1] | i is even }
		var domain = [radius, 1 - radius], measure = 1 - radius2, spline = [0, 1];
		while (measure) {
			var dart = measure * random(), i, l, interval, a, b, c, d;

			// Find where dart lies
			for (i = 0, l = domain.length, measure = 0; i < l; i += 2) {
				a = domain[i], b = domain[i + 1], interval = b - a;
				if (dart < measure + interval) {
					spline.push(dart += a - measure);
					break;
				}
				measure += interval;
			}
			c = dart - radius, d = dart + radius;

			// Update the domain
			for (i = domain.length - 1; i > 0; i -= 2) {
				l = i - 1, a = domain[l], b = domain[i];
				// c---d          c---d  Do nothing
				//   c-----d  c-----d    Move interior
				//   c--------------d    Delete interval
				//         c--d          Split interval
				//       a------b
				if (a >= c && a < d)
					if (b > d) domain[l] = d; // Move interior (Left case)
					else domain.splice(l, 2); // Delete interval
				else if (a < c && b > c)
					if (b <= d) domain[i] = c; // Move interior (Right case)
					else domain.splice(i, 0, c, d); // Split interval
			}

			// Re-measure the domain
			for (i = 0, l = domain.length, measure = 0; i < l; i += 2)
				measure += domain[i + 1] - domain[i];
		}

		return spline.sort();
	}

	// Create the overarching container
	var container = document.createElement('div');
	container.style.position = 'fixed';
	container.style.top = '0';
	container.style.left = '0';
	container.style.width = '100%';
	container.style.height = '0';
	container.style.overflow = 'visible';
	container.style.zIndex = '9999';

	// Confetto constructor
	function Confetto(theme) {
		this.frame = 0;
		this.outer = document.createElement('div');
		this.inner = document.createElement('div');
		this.outer.appendChild(this.inner);

		var outerStyle = this.outer.style, innerStyle = this.inner.style;
		outerStyle.position = 'absolute';
		outerStyle.width = (sizeMin + sizeMax * random()) + 'px';
		outerStyle.height = (sizeMin + sizeMax * random()) + 'px';
		innerStyle.width = '100%';
		innerStyle.height = '100%';
		innerStyle.backgroundColor = theme();

		outerStyle.perspective = '50px';
		outerStyle.transform = 'rotate(' + (360 * random()) + 'deg)';
		this.axis = 'rotate3D(' +
			cos(360 * random()) + ',' +
			cos(360 * random()) + ',0,';
		this.theta = 360 * random();
		this.dTheta = dThetaMin + dThetaMax * random();
		innerStyle.transform = this.axis + this.theta + 'deg)';

		this.x = window.innerWidth * random();
		this.y = -deviation;
		this.dx = sin(dxThetaMin + dxThetaMax * random());
		this.dy = dyMin + dyMax * random();
		outerStyle.left = this.x + 'px';
		outerStyle.top = this.y + 'px';

		// Create the periodic spline
		this.splineX = createPoisson();
		this.splineY = [];
		for (var i = 1, l = this.splineX.length - 1; i < l; ++i)
			this.splineY[i] = deviation * random();
		this.splineY[0] = this.splineY[l] = deviation * random();

		this.update = function (height, delta) {
			this.frame += delta;
			this.x += this.dx * delta;
			this.y += this.dy * delta;
			this.theta += this.dTheta * delta;

			// Compute spline and convert to polar
			var phi = this.frame % 7777 / 7777, i = 0, j = 1;
			while (phi >= this.splineX[j]) i = j++;
			var rho = interpolation(
				this.splineY[i],
				this.splineY[j],
				(phi - this.splineX[i]) / (this.splineX[j] - this.splineX[i])
			);
			phi *= PI2;

			outerStyle.left = this.x + rho * cos(phi) + 'px';
			outerStyle.top = this.y + rho * sin(phi) + 'px';
			innerStyle.transform = this.axis + this.theta + 'deg)';
			return this.y > height + deviation;
		};
	}

	function poof() {
		if (!frame) {
			// Append the container
			document.body.appendChild(container);

			// Add confetti
			var theme = colorThemes[0]
				, count = 0;
			(function addConfetto() {
				var confetto = new Confetto(theme);
				confetti.push(confetto);
				container.appendChild(confetto.outer);
				timer = setTimeout(addConfetto, spread * random());
			})(0);

			// Start the loop
			var prev = undefined;
			requestAnimationFrame(function loop(timestamp) {
				var delta = prev ? timestamp - prev : 0;
				prev = timestamp;
				var height = window.innerHeight;

				for (var i = confetti.length - 1; i >= 0; --i) {
					if (confetti[i].update(height, delta)) {
						container.removeChild(confetti[i].outer);
						confetti.splice(i, 1);
					}
				}

				if (timer || confetti.length)
					return frame = requestAnimationFrame(loop);

				// Cleanup
				document.body.removeChild(container);
				frame = undefined;
			});
		}
	}

	poof();
};

