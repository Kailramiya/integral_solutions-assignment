
from flask import Blueprint, request
from flask_jwt_extended import (
	create_access_token,
	create_refresh_token,
	get_jwt_identity,
	jwt_required,
)
from pymongo.errors import DuplicateKeyError

from app.extensions import mongo
from models.user_model import UserModel

auth_bp = Blueprint("auth", __name__)


@auth_bp.post("/signup")
def signup():
	payload = request.get_json(silent=True) or {}
	name = payload.get("name", "")
	email = payload.get("email", "")
	password = payload.get("password", "")

	UserModel.ensure_indexes(mongo)
	try:
		user_id = UserModel.create_user(mongo, name=name, email=email, plain_password=password)
	except DuplicateKeyError:
		return {"error": "email already exists"}, 409
	except ValueError as exc:
		return {"error": str(exc)}, 400
	except Exception:
		return {"error": "internal server error"}, 500

	access_token = create_access_token(identity=str(user_id))
	refresh_token = create_refresh_token(identity=str(user_id))
	return {"access_token": access_token, "refresh_token": refresh_token}, 201


@auth_bp.post("/login")
def login():
	payload = request.get_json(silent=True) or {}
	email = payload.get("email", "")
	password = payload.get("password", "")

	user = UserModel.get_by_email(mongo, email)
	if not user:
		return {"error": "invalid credentials"}, 401

	from models.user_model import User

	if not User.verify_password(password, user.password_hash):
		return {"error": "invalid credentials"}, 401

	access_token = create_access_token(identity=str(user._id))
	refresh_token = create_refresh_token(identity=str(user._id))
	return {"access_token": access_token, "refresh_token": refresh_token}, 200


@auth_bp.post("/refresh")
@jwt_required(refresh=True)
def refresh():
	user_id = get_jwt_identity()
	access_token = create_access_token(identity=str(user_id))
	return {"access_token": access_token}, 200


@auth_bp.get("/me")
@jwt_required()
def me():
	user_id = get_jwt_identity()
	user = UserModel.get_by_id(mongo, user_id)
	if not user:
		return {"error": "user not found"}, 404
	return {"user": UserModel.public_dict(user)}, 200


