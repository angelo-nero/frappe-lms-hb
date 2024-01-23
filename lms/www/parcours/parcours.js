let currentYear = new Date().getFullYear(); // Current year
let currentMonth = new Date().getMonth() + 1; // Current month (JavaScript months are 0-indexed)
let taggedDateRanges = [];

frappe.ready(() => {
    $(".menu-main > li").click((e) => {
        if (e.currentTarget.attributes['data-link'].value == 'forum')
            document.location.href = '/forum'
        else
            document.location.href = '/parcours?xsaoaz=' + e.currentTarget.attributes['data-link'].value
    });

    if (myJsTab == "parcours") {
        $(".module-item").click((e) => {
            $(".module-item-active").removeClass('module-item-active');
            $(".module-training.actif").removeClass('actif');
            e.currentTarget.classList.add('module-item-active');
            let current_module = e.currentTarget.attributes['data-module'].value
            $("div[data-trainning='" + current_module + "']").addClass('actif');
        });
        $(".module-tab>.module-item:first-child").click();
    } else if (myJsTab == "dashboard") {
        updateCalendar();
    } else if (myJsTab == "biblio-dtl") {
        // Call the function to populate tabs with JSON data
        populateTabs();
        // Open the first tab by default
        document.querySelector('.tablinks').click();
    }

})
let currCCSlide = 1;
let currCSSlide = 1;
const CCSLIDE_LENGTH = $('.cc-sld').length;
const CSSLIDE_LENGTH = $('.cs-sld').length;

function next(a) {
    let currSlide;
    if (a == "cs-sld") {
        currCSSlide = currCSSlide === CSSLIDE_LENGTH ? 1 : ++currCSSlide;
        currSlide = currCSSlide * 220;
    }
    else {
        currCCSlide = currCCSlide === CCSLIDE_LENGTH ? 1 : ++currCCSlide;
        currSlide = currCSSlide * 220;
    }
    $('.' + a + '-p').animate({
        scrollLeft: currSlide
    },
        'slow');
}

function previous(a) {
    let currSlide;
    if (a == "cs-sld") {
        currCSSlide = currCSSlide === 0 ? 1 : --currCSSlide;
        currSlide = currCSSlide * 220;
    }
    else {
        currCCSlide = currCCSlide === 0 ? 1 : --currCCSlide;
        currSlide = currCSSlide * 220;
    }
    $('.' + a + '-p').animate({
        scrollLeft: currSlide
    },
        'slow');
}

function createCalendar(year, month) {
    const days = ["Dim", "Lun", "Mar", "Mer", "Jeu", "Ven", "Sam"];
    const monthLength = new Date(year, month, 0).getDate();
    let table = `<table id='calendar'><tr><th>${days.join("</th><th>")}</th></tr><tr>`;

    let day = 1;
    const firstDay = new Date(year, month - 1, 1).getDay();

    for (let i = 0; i < 7; i++) {
        if (i < firstDay) {
            table += "<td></td>";
        } else {
            let fullDate = new Date(year, month - 1, day);
            let isWeekend = fullDate.getDay() === 0 || fullDate.getDay() === 6;
            table += `<td class='${isTaggedDate(fullDate) ? "tagged-date" : ""} ${isWeekend ? "weekend" : ""}'>${day++}</td>`;
        }
    }

    while (day <= monthLength) {
        table += "</tr><tr>";
        for (let i = 0; i < 7 && day <= monthLength; i++) {
            let fullDate = new Date(year, month - 1, day);
            let isWeekend = fullDate.getDay() === 0 || fullDate.getDay() === 6;
            table += `<td class='${isTaggedDate(fullDate) ? "tagged-date" : ""} ${isWeekend ? "weekend" : ""}'>${day++}</td>`;
        }
    }

    table += '</tr></table>';
    return table;
}

function isTaggedDate(date) {
    return taggedDateRanges.some(range =>
        date >= range.start && date <= range.end
    );
}

function updateMonthYearDisplay() {
    const monthNames = ["Janvier", "Février", "Mars", "Avril", "Mai", "Juin",
        "Juillet", "Août", "Septembre", "Octobre", "Novembre", "Décembre"];
    document.getElementById("currentMonthYear").textContent = `${monthNames[currentMonth - 1]} ${currentYear}`;
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

                taggedDateRanges.push({ start: startDate, end: endDate });
            });
            document.getElementById("calendar").innerHTML = createCalendar(currentYear, currentMonth);
        },
    });
}


function openTab(evt, tabName) {
    var i, tabcontent, tablinks;
    tabcontent = document.getElementsByClassName("tabcontent");
    for (i = 0; i < tabcontent.length; i++) {
        tabcontent[i].style.display = "none";
    }
    tablinks = document.getElementsByClassName("tablinks");
    for (i = 0; i < tablinks.length; i++) {
        tablinks[i].className = tablinks[i].className.replace(" active", "");
    }
    document.getElementById(tabName).style.display = "block";
    evt.currentTarget.className += " active";
}

function populateTabs() {
    ['stage_report', 'technic_doc', 'inter_pub'].forEach(tab => {
        var content = myJsBiblio[tab].map(item => `<p>${item.label}</p>`).join("");
        document.getElementById(tab).innerHTML = content;
    });
}

