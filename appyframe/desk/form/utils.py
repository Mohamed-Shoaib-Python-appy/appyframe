# Copyright (c) 2015, Appyframe Technologies Pvt. Ltd. and Contributors
# License: MIT. See LICENSE

import json
from typing import TYPE_CHECKING

import appyframe
import appyframe.desk.form.load
import appyframe.desk.form.meta
from appyframe import _
from appyframe.core.doctype.file.utils import extract_images_from_html
from appyframe.desk.form.document_follow import follow_document

if TYPE_CHECKING:
	from appyframe.core.doctype.comment.comment import Comment


@appyframe.whitelist(methods=["DELETE", "POST"])
def remove_attach():
	"""remove attachment"""
	fid = appyframe.form_dict.get("fid")
	appyframe.delete_doc("File", fid)


@appyframe.whitelist(methods=["POST", "PUT"])
def add_comment(
	reference_doctype: str, reference_name: str, content: str, comment_email: str, comment_by: str
) -> "Comment":
	"""Allow logged user with permission to read document to add a comment"""
	reference_doc = appyframe.get_doc(reference_doctype, reference_name)
	reference_doc.check_permission()

	comment = appyframe.new_doc("Comment")
	comment.update(
		{
			"comment_type": "Comment",
			"reference_doctype": reference_doctype,
			"reference_name": reference_name,
			"comment_email": comment_email,
			"comment_by": comment_by,
			"content": extract_images_from_html(reference_doc, content, is_private=True),
		}
	)
	comment.insert(ignore_permissions=True)

	if appyframe.get_cached_value("User", appyframe.session.user, "follow_commented_documents"):
		follow_document(comment.reference_doctype, comment.reference_name, appyframe.session.user)

	return comment


@appyframe.whitelist()
def update_comment(name, content):
	"""allow only owner to update comment"""
	doc = appyframe.get_doc("Comment", name)

	if appyframe.session.user not in ["Administrator", doc.owner]:
		appyframe.throw(_("Comment can only be edited by the owner"), appyframe.PermissionError)

	if doc.reference_doctype and doc.reference_name:
		reference_doc = appyframe.get_doc(doc.reference_doctype, doc.reference_name)
		reference_doc.check_permission()

		doc.content = extract_images_from_html(reference_doc, content, is_private=True)
	else:
		doc.content = content

	doc.save(ignore_permissions=True)


@appyframe.whitelist()
def get_next(doctype, value, prev, filters=None, sort_order="desc", sort_field="modified"):
	prev = int(prev)
	if not filters:
		filters = []
	if isinstance(filters, str):
		filters = json.loads(filters)

	# # condition based on sort order
	condition = ">" if sort_order.lower() == "asc" else "<"

	# switch the condition
	if prev:
		sort_order = "asc" if sort_order.lower() == "desc" else "desc"
		condition = "<" if condition == ">" else ">"

	# # add condition for next or prev item
	filters.append([doctype, sort_field, condition, appyframe.get_value(doctype, value, sort_field)])

	res = appyframe.get_list(
		doctype,
		fields=["name"],
		filters=filters,
		order_by=f"`tab{doctype}`.{sort_field}" + " " + sort_order,
		limit_start=0,
		limit_page_length=1,
		as_list=True,
	)

	if not res:
		appyframe.msgprint(_("No further records"))
		return None
	else:
		return res[0][0]


def get_pdf_link(doctype, docname, print_format="Standard", no_letterhead=0):
	return f"/api/method/appyframe.utils.print_format.download_pdf?doctype={doctype}&name={docname}&format={print_format}&no_letterhead={no_letterhead}"
