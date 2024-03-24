import frappe
from frappe.core.doctype.file.file import File as FrappeFile
img_exts = (
    '.mp4'
)

class LMSFile(FrappeFile):
    def is_downloadable(self):
        if not self.file_url.endswith(img_exts) or frappe.local.session.user == 'Guest':
            return super().is_downloadable()
        # User is authenticated, so can access files
        return True