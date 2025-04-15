import appyframe


def execute():
	appyframe.delete_doc_if_exists("DocType", "Tag Category")
	appyframe.delete_doc_if_exists("DocType", "Tag Doc Category")

	appyframe.reload_doc("desk", "doctype", "tag")
	appyframe.reload_doc("desk", "doctype", "tag_link")

	tag_list = []
	tag_links = []
	time = appyframe.utils.get_datetime()

	for doctype in appyframe.get_list("DocType", filters={"istable": 0, "issingle": 0, "is_virtual": 0}):
		if not appyframe.db.count(doctype.name) or not appyframe.db.has_column(doctype.name, "_user_tags"):
			continue

		for _user_tags in appyframe.db.sql(
			f"select `name`, `_user_tags` from `tab{doctype.name}`", as_dict=True
		):
			if not _user_tags.get("_user_tags"):
				continue

			for tag in _user_tags.get("_user_tags").split(",") if _user_tags.get("_user_tags") else []:
				if not tag:
					continue

				tag_list.append((tag.strip(), time, time, "Administrator"))

				tag_link_name = appyframe.generate_hash(length=10)
				tag_links.append(
					(tag_link_name, doctype.name, _user_tags.name, tag.strip(), time, time, "Administrator")
				)

	appyframe.db.bulk_insert(
		"Tag",
		fields=["name", "creation", "modified", "modified_by"],
		values=set(tag_list),
		ignore_duplicates=True,
	)
	appyframe.db.bulk_insert(
		"Tag Link",
		fields=["name", "document_type", "document_name", "tag", "creation", "modified", "modified_by"],
		values=set(tag_links),
		ignore_duplicates=True,
	)
