import hashlib
from passlib.context import CryptContext

pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)

def _pre_hash_password(password: str) -> str:
    """Pre-hash password with SHA256 to handle passwords > 72 bytes (bcrypt limit)"""
    return hashlib.sha256(password.encode()).hexdigest()

# Hash Password
def hash_password(password: str):
    pre_hashed = _pre_hash_password(password)
    return pwd_context.hash(pre_hashed)

# Verify Password
def verify_password(plain_password: str, hashed_password: str):
    pre_hashed = _pre_hash_password(plain_password)
    return pwd_context.verify(
        pre_hashed,
        hashed_password
    )