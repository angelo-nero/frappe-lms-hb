let currentYear = new Date().getFullYear(); // Current year
let currentMonth = new Date().getMonth() + 1; // Current month (JavaScript months are 0-indexed)
let taggedDateRanges = [];
const monthNames = ["Janvier", "Février", "Mars", "Avril", "Mai", "Juin",
    "Juillet", "Août", "Septembre", "Octobre", "Novembre", "Décembre"];

frappe.ready(() => {
    $(".menu-main > li").click((e) => {
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
                <div class='desc'>
                    ${isTaggedDate(fullDate)}
                </div>
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
    const dateWithoutTime = new Date(date.getFullYear(), date.getMonth(), date.getDate()); // Strip time components
    taggedDateRanges.forEach(range => {
        const rangeStartWithoutTime = new Date(range.start.getFullYear(), range.start.getMonth(), range.start.getDate());
        const rangeEndWithoutTime = new Date(range.end.getFullYear(), range.end.getMonth(), range.end.getDate());

        if (dateWithoutTime >= rangeStartWithoutTime && dateWithoutTime <= rangeEndWithoutTime) {
            description += `<div class="desc-content">
                        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" class="feather feather-circle feather feather-circle shrink-0 h-4 text-black h-4 text-black"><circle cx="12" cy="12" r="10"></circle></svg>
                        <div class="flex flex-col whitespace-nowrap overflow-hidden">
                            <p class="font-medium text-sm text-gray-800 text-ellipsis">${range.description}</p>
                        </div>
                    </div>`;
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
