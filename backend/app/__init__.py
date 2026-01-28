
import os
from pathlib import Path
from datetime import timedelta

from dotenv import load_dotenv
from flask import Flask

from .config import CONFIG_BY_NAME
from .extensions import jwt, mongo


def create_app(config_name: str | None = None) -> Flask:
	# Local development convenience; in prod env vars are usually provided by the host.
	backend_dir = Path(__file__).resolve().parent.parent
	load_dotenv(dotenv_path=backend_dir / ".env")

	app = Flask(__name__)

	env_name = (
		config_name
		or os.getenv("APP_ENV")
		or os.getenv("FLASK_ENV")
		or "development"
	).lower()
	config_cls = CONFIG_BY_NAME.get(env_name, CONFIG_BY_NAME["development"])
	app.config.from_object(config_cls)

	# Apply env-driven config AFTER dotenv is loaded.
	app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", app.config.get("SECRET_KEY", "dev"))
	app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY", app.config["SECRET_KEY"])
	app.config["MONGO_URI"] = os.getenv("MONGO_URI", "")
	app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(
		minutes=int(os.getenv("JWT_ACCESS_TOKEN_EXPIRES_MINUTES", "15"))
	)
	app.config["JWT_REFRESH_TOKEN_EXPIRES"] = timedelta(
		days=int(os.getenv("JWT_REFRESH_TOKEN_EXPIRES_DAYS", "7"))
	)

	app.config["PLAYBACK_TOKEN_SALT"] = os.getenv("PLAYBACK_TOKEN_SALT", "playback")
	app.config["PLAYBACK_TOKEN_EXPIRES_SECONDS"] = int(
		os.getenv("PLAYBACK_TOKEN_EXPIRES_SECONDS", "900")
	)

	if env_name == "testing":
		app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(minutes=1)
		app.config["JWT_REFRESH_TOKEN_EXPIRES"] = timedelta(minutes=5)

	if not app.config.get("MONGO_URI"):
		raise RuntimeError(
			"MONGO_URI is not set. Add it to backend/.env or your environment."
		)

	mongo.init_app(app)
	jwt.init_app(app)

	from routes.auth_routes import auth_bp
	from routes.dashboard_routes import dashboard_bp
	from routes.video_routes import video_bp
	from routes.stream_routes import stream_bp

	app.register_blueprint(auth_bp, url_prefix="/auth")
	app.register_blueprint(dashboard_bp, url_prefix="/dashboard")
	app.register_blueprint(video_bp, url_prefix="/videos")
	app.register_blueprint(stream_bp, url_prefix="/video")

	@app.get("/health")
	def health():
		return {"status": "ok", "env": env_name}

	return app


