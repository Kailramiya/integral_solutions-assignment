
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any

from bson import ObjectId
from bson.errors import InvalidId
import bcrypt


@dataclass(frozen=True, slots=True)
class User:
	name: str
	email: str
	password_hash: str
	created_at: datetime
	_id: ObjectId | None = None

	@staticmethod
	def hash_password(plain_password: str) -> str:
		if not plain_password or not plain_password.strip():
			raise ValueError("Password must not be empty")
		pw_bytes = plain_password.encode("utf-8")
		if len(pw_bytes) > 72:
			raise ValueError("password must not be longer than 72 bytes")
		hashed = bcrypt.hashpw(pw_bytes, bcrypt.gensalt())
		return hashed.decode("utf-8")

	@staticmethod
	def verify_password(plain_password: str, password_hash: str) -> bool:
		if not password_hash:
			return False
		try:
			return bcrypt.checkpw(
				plain_password.encode("utf-8"),
				password_hash.encode("utf-8"),
			)
		except Exception:
			return False

	def to_mongo(self) -> dict[str, Any]:
		doc: dict[str, Any] = {
			"name": self.name,
			"email": self.email,
			"password_hash": self.password_hash,
			"created_at": self.created_at,
		}
		if self._id is not None:
			doc["_id"] = self._id
		return doc

	@staticmethod
	def from_mongo(doc: dict[str, Any]) -> "User":
		return User(
			_id=doc.get("_id"),
			name=doc.get("name", ""),
			email=doc.get("email", ""),
			password_hash=doc.get("password_hash", ""),
			created_at=doc.get("created_at") or datetime.utcnow(),
		)


class UserModel:
	"""MongoDB access helpers for users."""

	COLLECTION_NAME = "users"

	@staticmethod
	def normalize_email(email: str) -> str:
		return (email or "").strip().lower()

	@classmethod
	def ensure_indexes(cls, mongo) -> None:
		mongo.db[cls.COLLECTION_NAME].create_index("email", unique=True)

	@classmethod
	def get_by_email(cls, mongo, email: str) -> User | None:
		doc = mongo.db[cls.COLLECTION_NAME].find_one({"email": cls.normalize_email(email)})
		return User.from_mongo(doc) if doc else None

	@classmethod
	def get_by_id(cls, mongo, user_id: str | ObjectId) -> User | None:
		try:
			oid = user_id if isinstance(user_id, ObjectId) else ObjectId(str(user_id))
		except (InvalidId, TypeError, ValueError):
			return None
		doc = mongo.db[cls.COLLECTION_NAME].find_one({"_id": oid})
		return User.from_mongo(doc) if doc else None

	@staticmethod
	def public_dict(user: User) -> dict[str, Any]:
		created_at = user.created_at
		return {
			"id": str(user._id) if user._id is not None else None,
			"name": user.name,
			"email": user.email,
			"created_at": created_at.isoformat() if hasattr(created_at, "isoformat") else created_at,
		}

	@classmethod
	def create_user(cls, mongo, name: str, email: str, plain_password: str) -> ObjectId:
		normalized_email = cls.normalize_email(email)
		if not normalized_email:
			raise ValueError("Email must not be empty")

		password_hash = User.hash_password(plain_password)
		user = User(
			name=(name or "").strip(),
			email=normalized_email,
			password_hash=password_hash,
			created_at=datetime.utcnow(),
		)
		result = mongo.db[cls.COLLECTION_NAME].insert_one(user.to_mongo())
		return result.inserted_id

