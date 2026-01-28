from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv


def _load_env() -> None:
	backend_dir = Path(__file__).resolve().parents[1]
	load_dotenv(dotenv_path=backend_dir / ".env")


def main() -> int:
	_load_env()

	mongo_uri = os.getenv("MONGO_URI", "").strip()
	if not mongo_uri:
		raise SystemExit("MONGO_URI is not set. Add it to backend/.env")

	try:
		from pymongo import MongoClient
	except Exception as exc:
		raise SystemExit(
			"pymongo is required (installed via Flask-PyMongo). Try: pip install -r backend/requirements.txt"
		) from exc

	client = MongoClient(mongo_uri)
	# Use the database from the URI if provided; otherwise fall back to env/constant.
	try:
		db = client.get_default_database()
	except Exception:
		db = None
	if db is None:
		db = client[os.getenv("MONGO_DB", "integral-solution")]
	collection = db["videos"]

	items = [
		{
			"title": "Big Buck Bunny (Sample)",
			"description": "A public sample MP4 that plays reliably in mobile players.",
			"youtube_id": "sample1",
			"video_url": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4",
			"thumbnail_url": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/images/BigBuckBunny.jpg",
			"is_active": True,
		},
		{
			"title": "Elephant Dream (Sample)",
			"description": "Another public sample MP4 for testing dashboard and playback.",
			"youtube_id": "sample2",
			"video_url": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ElephantsDream.mp4",
			"thumbnail_url": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/images/ElephantsDream.jpg",
			"is_active": True,
		},
	]

	# Idempotent: upsert by youtube_id.
	upserted = 0
	updated = 0
	for item in items:
		result = collection.update_one(
			{"youtube_id": item["youtube_id"]},
			{"$set": item},
			upsert=True,
		)
		if result.upserted_id is not None:
			upserted += 1
			print(f"Inserted: {item['youtube_id']}")
		elif result.modified_count:
			updated += 1
			print(f"Updated:  {item['youtube_id']}")
		else:
			print(f"Unchanged: {item['youtube_id']}")

	print(
		f"Done. upserted={upserted} updated={updated} total={len(items)}. "
		"Your /dashboard endpoint will return up to 2 active videos."
	)
	return 0


if __name__ == "__main__":
	raise SystemExit(main())
