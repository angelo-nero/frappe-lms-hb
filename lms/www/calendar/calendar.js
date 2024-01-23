let currentYear = new Date().getFullYear(); // Current year
let currentMonth = new Date().getMonth() + 1; // Current month (JavaScript months are 0-indexed)
let taggedDateRanges = [];
const monthNames = ["Janvier", "Février", "Mars", "Avril", "Mai", "Juin",
    "Juillet", "Août", "Septembre", "Octobre", "Novembre", "Décembre"];

frappe.ready(() => {
    $(".menu-main > li").click((e) => {
        if (e.currentTarget.attributes['data-link'].value == 'forum')
            document.location.href = '/forum'
        else
            document.location.href = '/parcours?xsaoaz=' + e.currentTarget.attributes['data-link'].value
    });
    updateCalendar();
})


function createCalendar(year, month) {
    const days = ["Dimanche", "Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi"];
    const monthLength = new Date(year, month, 0).getDate();
    let table = `<table id='calendar'><tr><th>${days.join("</th><th>")}</th></tr><tr>`;

    let day = 1;
    const firstDay = new Date(year, month - 1, 1).getDay();

    for (let i = 0; i < 7; i++) {
        if (i < firstDay) {
            table += "<td class='over-day'></td>";
        } else {
            let fullDate = new Date(year, month - 1, day);
            let isWeekend = fullDate.getDay() === 0 || fullDate.getDay() === 6;
            table += `<td class='${isWeekend ? "weekend" : ""}'>
            <span class='day'>${day++}</span>
            <span class='desc'>${isTaggedDate(fullDate)}</span>
            </td>`;
        }
    }

    while (day <= monthLength) {
        table += "</tr><tr>";
        for (let i = 0; i < 7; i++) {
            if (day <= monthLength) {
                let fullDate = new Date(year, month - 1, day);
                let isWeekend = fullDate.getDay() === 0 || fullDate.getDay() === 6;
                table += `<td class='${isWeekend ? "weekend" : ""}'>
                <span class='day'>${day++}</span>
                <span class='desc'>${isTaggedDate(fullDate)}</span>
            </td>`;
            } else {
                table += `<td class='over-day'></td>`;
            }
        }
    }

    table += '</tr></table>';
    return table;
}

function isTaggedDate(date) {
    let description = ''
    taggedDateRanges.forEach(range => {
        if (date >= range.start && date <= range.end) {
            description += '- ' + range.description + '<br/>';
        }
    });

    return description;
}

function updateMonthYearDisplay() {
    document.getElementById("currentMonthYear").textContent = `${monthNames[currentMonth === 0 ? 11 : currentMonth - 1]} ${currentYear}`;
}

function updateCalendar() {
    updateMonthYearDisplay();
    let now = new Date();
    let firstDayOfMonth = new Date(now.getFullYear(), now.getMonth(), 1);
    let lastDayOfMonth = new Date(now.getFullYear(), now.getMonth() + 1);
    frappe.call({
        method: "frappe.desk.calendar.get_events",
        type: "GET",
        args: {
            doctype: 'LMS Class',
            start: firstDayOfMonth.toISOString(),
            end: lastDayOfMonth.toISOString(),
            field_map: { "id": "name", "start": "start_date", "end": "end_date", "title": "description", "allDay": 1 }
        },
        callback: function (r) {
            r.message.forEach(item => {
                const startDate = new Date(item.start_date);
                const endDate = new Date(item.end_date);
                const description = item.description;

                taggedDateRanges.push({ start: startDate, end: endDate, description: description });
            });
            document.getElementById("calendar").innerHTML = createCalendar(currentYear, currentMonth);
        },
    });
}

document.getElementById("prevMonth").addEventListener("click", function () {
    currentMonth--;
    if (currentMonth < 0) {
        currentMonth = 11;
        currentYear--;
    }

    document.getElementById("calendar").innerHTML = createCalendar(currentYear, currentMonth); updateMonthYearDisplay()
});

document.getElementById("nextMonth").addEventListener("click", function () {
    currentMonth++;
    if (currentMonth > 11) {
        currentMonth = 0;
        currentYear++;
    }
    document.getElementById("calendar").innerHTML = createCalendar(currentYear, currentMonth); updateMonthYearDisplay()
});
