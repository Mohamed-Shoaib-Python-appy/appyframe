import json
from typing import TYPE_CHECKING, Union

import redis

import appyframe
from appyframe.utils import cstr

if TYPE_CHECKING:
	from appyframe.model.document import Document

queue_prefix = "insert_queue_for_"


def deferred_insert(doctype: str, records: list[Union[dict, "Document"]] | str):
	if isinstance(records, dict | list):
		_records = json.dumps(records)
	else:
		_records = records

	try:
		appyframe.cache.rpush(f"{queue_prefix}{doctype}", _records)
	except redis.exceptions.ConnectionError:
		for record in records:
			insert_record(record, doctype)


def save_to_db():
	queue_keys = appyframe.cache.get_keys(queue_prefix)
	for key in queue_keys:
		record_count = 0
		queue_key = get_key_name(key)
		doctype = get_doctype_name(key)
		while appyframe.cache.llen(queue_key) > 0 and record_count <= 500:
			records = appyframe.cache.lpop(queue_key)
			records = json.loads(records.decode("utf-8"))
			if isinstance(records, dict):
				record_count += 1
				insert_record(records, doctype)
				continue
			for record in records:
				record_count += 1
				insert_record(record, doctype)


def insert_record(record: Union[dict, "Document"], doctype: str):
	try:
		record.update({"doctype": doctype})
		appyframe.get_doc(record).insert()
	except Exception as e:
		appyframe.logger().error(f"Error while inserting deferred {doctype} record: {e}")


def get_key_name(key: str) -> str:
	return cstr(key).split("|")[1]


def get_doctype_name(key: str) -> str:
	return cstr(key).split(queue_prefix)[1]
