
from __future__ import annotations

import time
from dataclasses import dataclass

from itsdangerous import BadSignature, URLSafeTimedSerializer


@dataclass(frozen=True, slots=True)
class PlaybackToken:
	token: str
	video_id: str
	exp: int


class PlaybackTokenService:
	def __init__(self, *, secret_key: str, salt: str = "playback") -> None:
		if not secret_key:
			raise ValueError("secret_key must not be empty")
		self._serializer = URLSafeTimedSerializer(secret_key=secret_key, salt=salt)

	def generate(self, *, video_id: str, expires_in_seconds: int) -> PlaybackToken:
		if not video_id:
			raise ValueError("video_id must not be empty")
		if expires_in_seconds <= 0:
			raise ValueError("expires_in_seconds must be > 0")

		exp = int(time.time()) + int(expires_in_seconds)
		payload = {"video_id": str(video_id), "exp": exp}
		token = self._serializer.dumps(payload)
		return PlaybackToken(token=token, video_id=str(video_id), exp=exp)

	def verify(self, token: str) -> str | None:
		if not token:
			return None
		try:
			data = self._serializer.loads(token)
		except BadSignature:
			return None

		video_id = str(data.get("video_id") or "")
		exp = data.get("exp")
		if not video_id or not isinstance(exp, int):
			return None
		if int(time.time()) > exp:
			return None
		return video_id

