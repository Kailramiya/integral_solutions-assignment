
from flask import Blueprint
from flask_jwt_extended import jwt_required

video_bp = Blueprint("videos", __name__)


@video_bp.get("/")
@jwt_required()
def list_videos():
	return {"items": []}

