# Copyright (c) 2023, Appyframe Technologies and contributors
# For license information, please see license.txt


import requests

import appyframe
from appyframe.model.document import Document
from appyframe.utils.caching import redis_cache
from appyframe.utils.data import add_to_date


class ChangelogFeed(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from appyframe.types import DF

		app_name: DF.Data | None
		link: DF.LongText
		posting_timestamp: DF.Datetime
		title: DF.Data
	# end: auto-generated types

	pass


def fetch_changelog_feed():
	"""Fetches changelog feed items from source using `get_changelog_feed` hook and stores in the db"""
	since = appyframe.db.get_value(
		"Changelog Feed",
		filters={},
		fieldname="posting_timestamp",
		order_by="posting_timestamp desc",
	) or add_to_date(None, months=-1, as_datetime=True, as_string=False)

	for fn in appyframe.get_hooks("get_changelog_feed"):
		try:
			cache_key = f"changelog_feed::{fn}"
			changelog_feed = appyframe.cache.get_value(cache_key, shared=True)
			if changelog_feed is None:
				changelog_feed = appyframe.call(fn, since=since)[:20] or []
				appyframe.cache.set_value(
					cache_key, changelog_feed, expires_in_sec=7 * 24 * 60 * 60, shared=True
				)

			for feed_item in changelog_feed:
				feed = {
					"title": feed_item["title"],
					"app_name": feed_item["app_name"],
					"link": feed_item["link"],
					"posting_timestamp": feed_item["creation"],
				}
				if not appyframe.db.exists("Changelog Feed", feed):
					appyframe.new_doc("Changelog Feed").update(feed).insert()
		except Exception:
			appyframe.log_error(f"Failed to fetch changelog from {fn}")
			# don't retry if it's broken for 1 week
			appyframe.cache.set_value(cache_key, [], expires_in_sec=7 * 24 * 60 * 60, shared=True)


@redis_cache
def get_changelog_feed_items():
	"""Returns a list of latest 10 changelog feed items"""
	feed = appyframe.get_all(
		"Changelog Feed",
		fields=["title", "app_name", "link", "posting_timestamp"],
		# allow pubishing feed for many apps with single hook
		filters={"app_name": ("in", appyframe.get_installed_apps())},
		order_by="posting_timestamp desc",
		limit=20,
	)
	for f in feed:
		f["app_title"] = _app_title(f["app_name"])

	return feed


def _app_title(app_name):
	try:
		return appyframe.get_hooks("app_title", app_name=app_name)[0]
	except Exception:
		return app_name


def get_feed(since):
	"""'What's New' feed implementation for Appyframe"""
	r = requests.get(f"https://appyframe.io/api/method/changelog_feed?since={since}")
	r.raise_for_status()
	return r.json()["message"]
