
from flask import Blueprint
from flask_jwt_extended import jwt_required

from app.extensions import mongo

dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.get("")
@jwt_required()
def dashboard_home():
	cursor = (
		mongo.db["videos"]
		.find(
			{"is_active": True},
			{"title": 1, "description": 1, "thumbnail_url": 1},
		)
		.sort("_id", -1)
		.limit(2)
	)

	items = [
		{
			"id": str(doc.get("_id")),
			"title": doc.get("title", ""),
			"description": doc.get("description", ""),
			"thumbnail_url": doc.get("thumbnail_url", ""),
		}
		for doc in cursor
	]
	return {"items": items}, 200


