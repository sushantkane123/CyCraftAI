"""Password hashing - bcrypt direct (avoids passlib/bcrypt version conflicts)."""
import bcrypt


def hash_password(plain: str) -> str:
    """Hash a plaintext password using bcrypt (cost factor 12)."""
    plain_bytes = plain.encode("utf-8")[:72]   # bcrypt limit
    salt = bcrypt.gensalt(rounds=12)
    return bcrypt.hashpw(plain_bytes, salt).decode("utf-8")


def verify_password(plain: str, hashed: str) -> bool:
    """Verify a plaintext password against a stored bcrypt hash."""
    if not hashed:
        return False
    try:
        plain_bytes = plain.encode("utf-8")[:72]
        return bcrypt.checkpw(plain_bytes, hashed.encode("utf-8"))
    except Exception:
        return False
