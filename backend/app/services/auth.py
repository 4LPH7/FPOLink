"""Authentication service — password hashing with Argon2 via pwdlib."""

from pwdlib import PasswordHash
from pwdlib.hashers.argon2 import Argon2Hasher

# Use Argon2id (recommended by OWASP)
pwd_hash = PasswordHash((Argon2Hasher(),))


def hash_password(password: str) -> str:
    """Hash a password using Argon2id."""
    return pwd_hash.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its Argon2id hash."""
    return pwd_hash.verify(plain_password, hashed_password)
