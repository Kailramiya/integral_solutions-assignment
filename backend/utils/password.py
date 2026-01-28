
import bcrypt


def hash_password(plain_password: str) -> str:
	pw_bytes = (plain_password or "").encode("utf-8")
	if len(pw_bytes) > 72:
		raise ValueError("password must not be longer than 72 bytes")
	hashed = bcrypt.hashpw(pw_bytes, bcrypt.gensalt())
	return hashed.decode("utf-8")


def verify_password(plain_password: str, password_hash: str) -> bool:
	try:
		return bcrypt.checkpw(
			(plain_password or "").encode("utf-8"),
			(password_hash or "").encode("utf-8"),
		)
	except Exception:
		return False

