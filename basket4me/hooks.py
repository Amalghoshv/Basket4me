app_name = "basket4me"
app_title = "Basket4Me"
app_publisher = "siva"
app_description = "Basket4me"
app_email = "sivajyothis9446@gmail.com"
app_license = "mit"
# required_apps = []

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/basket4me/css/basket4me.css"
# app_include_js = "/assets/basket4me/js/basket4me.js"

# include js, css files in header of web template
# web_include_css = "/assets/basket4me/css/basket4me.css"
# web_include_js = "/assets/basket4me/js/basket4me.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "basket4me/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Svg Icons
# ------------------
# include app icons in desk
# app_include_icons = "basket4me/public/icons.svg"

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
# 	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Jinja
# ----------

# add methods and filters to jinja environment
# jinja = {
# 	"methods": "basket4me.utils.jinja_methods",
# 	"filters": "basket4me.utils.jinja_filters"
# }

# Installation
# ------------

# before_install = "basket4me.install.before_install"
# after_install = "basket4me.install.after_install"

# Uninstallation
# ------------

# before_uninstall = "basket4me.uninstall.before_uninstall"
# after_uninstall = "basket4me.uninstall.after_uninstall"

# Integration Setup
# ------------------
# To set up dependencies/integrations with other apps
# Name of the app being installed is passed as an argument

# before_app_install = "basket4me.utils.before_app_install"
# after_app_install = "basket4me.utils.after_app_install"

# Integration Cleanup
# -------------------
# To clean up dependencies/integrations with other apps
# Name of the app being uninstalled is passed as an argument

# before_app_uninstall = "basket4me.utils.before_app_uninstall"
# after_app_uninstall = "basket4me.utils.after_app_uninstall"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "basket4me.notifications.get_notification_config"

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

# DocType Class
# ---------------
# Override standard doctype classes

# override_doctype_class = {
# 	"ToDo": "custom_app.overrides.CustomToDo"
# }

# Document Events
# ---------------
# Hook on document methods and events

# doc_events = {
# 	"*": {
# 		"on_update": "method",
# 		"on_cancel": "method",
# 		"on_trash": "method"
# 	}
# }

# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"basket4me.tasks.all"
# 	],
# 	"daily": [
# 		"basket4me.tasks.daily"
# 	],
# 	"hourly": [
# 		"basket4me.tasks.hourly"
# 	],
# 	"weekly": [
# 		"basket4me.tasks.weekly"
# 	],
# 	"monthly": [
# 		"basket4me.tasks.monthly"
# 	],sync_payment_entries_from_external_api
# }
scheduler_events = {
    "cron": {
        "*/2 * * * *": [
            "basket4me.external.sync_customers_from_external_api"
        ],
        "*/4 * * * *": [
            "basket4me.external.sync_items_from_external_api"
        ],
         "*/3 * * * *": [
            "basket4me.external.sync_sales_orders_from_external_api"
        ],
         "*/3 * * * *": [
            "basket4me.external.sync_sales_invoices_from_external_api"
        ],
         "*/3 * * * *": [
            "basket4me.external.sync_payment_entries_from_external_api"
        ]
    }
}

# Testing
# -------

# before_tests = "basket4me.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "basket4me.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "basket4me.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]

# Request Events
# ----------------
# before_request = ["basket4me.utils.before_request"]
# after_request = ["basket4me.utils.after_request"]

# Job Events
# ----------
# before_job = ["basket4me.utils.before_job"]
# after_job = ["basket4me.utils.after_job"]

# User Data Protection
# --------------------

# user_data_fields = [
# 	{
# 		"doctype": "{doctype_1}",
# 		"filter_by": "{filter_by}",
# 		"redact_fields": ["{field_1}", "{field_2}"],
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_2}",
# 		"filter_by": "{filter_by}",
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_3}",
# 		"strict": False,
# 	},
# 	{
# 		"doctype": "{doctype_4}"
# 	}
# ]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
# 	"basket4me.auth.validate"
# ]

# Automatically update python controller files with type annotations for this app.
# export_python_type_annotations = True

# default_log_clearing_doctypes = {
# 	"Logging DocType Name": 30  # days to retain logs
# }

