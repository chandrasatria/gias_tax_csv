# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from . import __version__ as app_version

app_name = "tax"
app_title = "Tax"
app_publisher = "Myme"
app_description = "Tax"
app_icon = "octicon octicon-file-directory"
app_color = "grey"
app_email = "technical@erpsonic.com"
app_license = "MIT"
# fixtures = ["Custom Field"]
# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/tax/css/tax.css"
# app_include_js = "/assets/tax/js/tax.js"

# include js, css files in header of web template
# web_include_css = "/assets/tax/css/tax.css"
# web_include_js = "/assets/tax/js/tax.js"

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
#	"Role": "home_page"
# }

# Website user home page (by function)
# get_website_user_home_page = "tax.utils.get_home_page"

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Installation
# ------------

# before_install = "tax.install.before_install"
# after_install = "tax.install.after_install"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "tax.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# Document Events
# ---------------
# Hook on document methods and events

#doc_events = {
#	"Sales Order": {
#		"validate": "tax.tes.tes",
# 		"on_cancel": "method",
# 		"on_trash": "method"
#	}
#}

doc_events = {
	"Sales Invoice": {

		"before_submit": ["tax.tax.doctype.custom_method_tax.isikan_nomor_faktur_pajak"],
		"on_submit": ["tax.tax.doctype.custom_method_tax.update_faktur_pajak_sales_invoice_on_submit"],
		"on_cancel": ["tax.tax.doctype.custom_method_tax.update_faktur_pajak_sales_invoice_on_cancel"],
		"before_update_after_submit" : ["tax.tax.doctype.custom_method_tax.cek_status"]
	
	
	},
	
}

# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"tax.tasks.all"
# 	],
# 	"daily": [
# 		"tax.tasks.daily"
# 	],
# 	"hourly": [
# 		"tax.tasks.hourly"
# 	],
# 	"weekly": [
# 		"tax.tasks.weekly"
# 	]
# 	"monthly": [
# 		"tax.tasks.monthly"
# 	]
# }

# Testing
# -------

# before_tests = "tax.install.before_tests"

# Overriding Whitelisted Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "tax.event.get_events"
# }

