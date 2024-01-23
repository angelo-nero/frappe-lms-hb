frappe.ready(() => {
    $(".menu-main > li").click((e) => {
        if (e.currentTarget.attributes['data-link'].value == 'forum')
            document.location.href = '/forum'
        else
            document.location.href = '/parcours?xsaoaz=' + e.currentTarget.attributes['data-link'].value
    });
})