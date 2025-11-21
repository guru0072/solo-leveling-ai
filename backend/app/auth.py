from typing import Optional, Tuple
import uuid
import time

from passlib.context import CryptContext
import jwt

from .db import get_db_session

# ------------------------------
# Password hashing config
# ------------------------------

# WHAT: passlib's CryptContext handles hashing/verification.
# WHY: So we don't implement hashing by hand (bcrypt is tricky).
# HOW: We're telling it "use bcrypt".
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# ------------------------------
# JWT config
# ------------------------------

# WHAT: Secret key + algorithm + expiry.
# WHY: Needed to sign and verify JWT tokens.
# HOW: In production this SECRET must come from environment, not hardcoded.
JWT_SECRET = "CHANGE_ME_TO_A_LONG_RANDOM_SECRET"
JWT_ALGO = "HS256"
JWT_EXP_SECONDS = 60 * 60 * 24 * 7  # 7 days


def hash_password(password: str) -> str:
    """
    WHAT: Hash a plain-text password using bcrypt.
    WHY: We NEVER store raw passwords in the database.
    HOW: passlib will salt + hash and return a string like $2b$12$...
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    WHAT: Compare user-entered password with stored hash.
    WHY: Used during login.
    HOW: passlib checks if plain_password matches hashed_password.
    """
    return pwd_context.verify(plain_password, hashed_password)


def create_jwt(user_id: str) -> str:
    """
    WHAT: Create a signed JWT token for this user ID.
    WHY: So client can prove who they are on later requests.
    HOW: Encode a payload with sub=user_id, iat, exp using HS256.
    """
    now = int(time.time())
    payload = {
        "sub": user_id,          # subject = user_id
        "iat": now,              # issued at
        "exp": now + JWT_EXP_SECONDS,  # expiry
    }
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGO)
    return token


def decode_jwt(token: str) -> Optional[dict]:
    """
    WHAT: Decode and verify a JWT token.
    WHY: Used in get_current_user() to extract the user id.
    HOW: Returns payload dict if valid, None if invalid/expired.
    """
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGO])
        return payload
    except jwt.PyJWTError:
        return None


def create_user(
    email: str,
    password: str,
    display_name: Optional[str] = None,
    height_cm: Optional[int] = None,
    weight_kg: Optional[float] = None,
    activity_level: str = "sedentary",
) -> str:
    """
    WHAT: Insert a new user row into the users table.
    WHY: Called from /auth/signup.
    HOW:
      1) Generate a unique user_id.
      2) Hash the password.
      3) INSERT into SQLite.
    """
    user_id = "user_" + uuid.uuid4().hex[:8]

    # CRITICAL: hash the plain password string here.
    password_hash = hash_password(password)

    with get_db_session() as conn:
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO users (id, email, display_name, password_hash, height_cm, weight_kg, activity_level)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (user_id, email, display_name, password_hash, height_cm, weight_kg, activity_level),
        )
        conn.commit()

    return user_id


def get_user_by_email(email: str) -> Optional[Tuple]:
    """
    WHAT: Fetch a single user row by email.
    WHY: Used in signup (to check duplicates) and login.
    HOW: Returns the SQLite row (tuple) or None if not found.
    """
    with get_db_session() as conn:
        cur = conn.cursor()
        cur.execute(
            """
            SELECT id, email, display_name, password_hash, height_cm, weight_kg, activity_level
            FROM users
            WHERE email = ?
            """,
            (email,),
        )
        row = cur.fetchone()
    return row
