"""Password hashing and registration for local demonstration."""
import hashlib, hmac, secrets, sqlite3
from database import connect

ITERATIONS = 310_000

def _hash_password(password):
    salt = secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, ITERATIONS)
    return "pbkdf2_sha256$" + str(ITERATIONS) + "$" + salt.hex() + "$" + digest.hex()

def _verify_password(password, encoded):
    try:
        algorithm, iterations, salt_hex, expected_hex = encoded.split("$")
        if algorithm != "pbkdf2_sha256":
            return False
        actual = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), bytes.fromhex(salt_hex), int(iterations))
        return hmac.compare_digest(actual, bytes.fromhex(expected_hex))
    except (ValueError, TypeError, AttributeError):
        return False

def register(username, password):
    username = username.strip()
    if not username or len(username) > 50:
        raise ValueError("Username must be 1–50 characters.")
    if len(password) < 8:
        raise ValueError("Password must contain at least 8 characters.")
    try:
        with connect() as db:
            db.execute("INSERT INTO users(username,password_hash) VALUES(?,?)", (username, _hash_password(password)))
        return True
    except sqlite3.IntegrityError:
        return False

def login(username, password):
    with connect() as db:
        row = db.execute("SELECT id,username,password_hash FROM users WHERE username=?", (username.strip(),)).fetchone()
    if row and _verify_password(password, row["password_hash"]):
        return (row["id"], row["username"])
    return None
