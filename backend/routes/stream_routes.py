import re
from urllib.parse import urlparse

from flask import Blueprint, current_app, request
from flask_jwt_extended import jwt_required

from app.extensions import mongo
from models.video_model import VideoModel
from services.token_service import PlaybackTokenService


stream_bp = Blueprint("stream", __name__)


_YOUTUBE_ID_RE = re.compile(r"^[A-Za-z0-9_-]{6,}$")


def _safe_http_url(url: str) -> str | None:
    url = (url or "").strip()
    if not url:
        return None
    try:
        parsed = urlparse(url)
    except Exception:
        return None
    if parsed.scheme not in {"http", "https"}:
        return None
    if not parsed.netloc:
        return None
    return url


def _embed_safe_youtube_url(youtube_id: str) -> str | None:
    youtube_id = (youtube_id or "").strip()
    if not _YOUTUBE_ID_RE.match(youtube_id):
        return None
    # Standard embed tends to work better in mobile WebViews than the nocookie domain.
    return f"https://www.youtube.com/embed/{youtube_id}"


def _watch_youtube_url(youtube_id: str) -> str | None:
    youtube_id = (youtube_id or "").strip()
    if not _YOUTUBE_ID_RE.match(youtube_id):
        return None
    return f"https://www.youtube.com/watch?v={youtube_id}"


@stream_bp.get("/<id>/stream")
def stream_video(id: str):
    token = request.args.get("token", "")

    service = PlaybackTokenService(
        secret_key=current_app.config["JWT_SECRET_KEY"],
        salt=current_app.config.get("PLAYBACK_TOKEN_SALT", "playback"),
    )
    token_video_id = service.verify(token)
    if not token_video_id:
        return {"error": "invalid or expired token"}, 401
    if str(token_video_id) != str(id):
        return {"error": "token does not match video"}, 403

    video = VideoModel.get_by_id(mongo, id)
    if not video or not video.is_active:
        return {"error": "video not found"}, 404

    # If the video has a direct URL (e.g. MP4), prefer that.
    direct_url = _safe_http_url(getattr(video, "video_url", None) or "")
    if direct_url:
        return {"url": direct_url, "watch_url": None, "stream_type": "mp4"}, 200

    url = _embed_safe_youtube_url(video.youtube_id)
    if not url:
        return {"error": "invalid youtube_id"}, 500

    watch_url = _watch_youtube_url(video.youtube_id)
    return {"url": url, "watch_url": watch_url, "stream_type": "embed"}, 200


@stream_bp.get("/<id>/token")
@jwt_required()
def mint_playback_token(id: str):
    video = VideoModel.get_by_id(mongo, id)
    if not video or not video.is_active:
        return {"error": "video not found"}, 404

    service = PlaybackTokenService(
        secret_key=current_app.config["JWT_SECRET_KEY"],
        salt=current_app.config.get("PLAYBACK_TOKEN_SALT", "playback"),
    )
    expires_in = int(current_app.config.get("PLAYBACK_TOKEN_EXPIRES_SECONDS", 900))
    playback = service.generate(video_id=id, expires_in_seconds=expires_in)
    return {"token": playback.token, "exp": playback.exp, "video_id": playback.video_id}, 200

