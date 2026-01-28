
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from bson import ObjectId
from bson.errors import InvalidId


@dataclass(frozen=True, slots=True)
class Video:
	title: str
	description: str
	youtube_id: str
	video_url: str | None
	thumbnail_url: str
	is_active: bool
	_id: ObjectId | None = None

	def to_mongo(self) -> dict[str, Any]:
		doc: dict[str, Any] = {
			"title": self.title,
			"description": self.description,
			"youtube_id": self.youtube_id,
			"video_url": self.video_url,
			"thumbnail_url": self.thumbnail_url,
			"is_active": self.is_active,
		}
		if self._id is not None:
			doc["_id"] = self._id
		return doc

	@staticmethod
	def from_mongo(doc: dict[str, Any]) -> "Video":
		return Video(
			_id=doc.get("_id"),
			title=doc.get("title", ""),
			description=doc.get("description", ""),
			youtube_id=doc.get("youtube_id", ""),
			video_url=doc.get("video_url") or None,
			thumbnail_url=doc.get("thumbnail_url", ""),
			is_active=bool(doc.get("is_active", True)),
		)


class VideoModel:
	"""MongoDB access helpers for videos."""

	COLLECTION_NAME = "videos"

	@staticmethod
	def normalize_youtube_id(youtube_id: str) -> str:
		return (youtube_id or "").strip()

	@classmethod
	def ensure_indexes(cls, mongo) -> None:
		mongo.db[cls.COLLECTION_NAME].create_index("youtube_id", unique=True)
		mongo.db[cls.COLLECTION_NAME].create_index("is_active")

	@classmethod
	def get_by_id(cls, mongo, video_id: str | ObjectId) -> Video | None:
		try:
			oid = video_id if isinstance(video_id, ObjectId) else ObjectId(str(video_id))
		except (InvalidId, TypeError, ValueError):
			return None
		doc = mongo.db[cls.COLLECTION_NAME].find_one({"_id": oid})
		return Video.from_mongo(doc) if doc else None

	@classmethod
	def get_by_youtube_id(cls, mongo, youtube_id: str) -> Video | None:
		normalized = cls.normalize_youtube_id(youtube_id)
		if not normalized:
			return None
		doc = mongo.db[cls.COLLECTION_NAME].find_one({"youtube_id": normalized})
		return Video.from_mongo(doc) if doc else None

	@classmethod
	def create_video(
		cls,
		mongo,
		*,
		title: str,
		description: str,
		youtube_id: str,
		video_url: str | None = None,
		thumbnail_url: str,
		is_active: bool = True,
	) -> ObjectId:
		normalized = cls.normalize_youtube_id(youtube_id)
		if not normalized:
			raise ValueError("youtube_id must not be empty")

		video = Video(
			title=(title or "").strip(),
			description=description or "",
			youtube_id=normalized,
			video_url=(video_url or "").strip() or None,
			thumbnail_url=(thumbnail_url or "").strip(),
			is_active=bool(is_active),
		)
		result = mongo.db[cls.COLLECTION_NAME].insert_one(video.to_mongo())
		return result.inserted_id

