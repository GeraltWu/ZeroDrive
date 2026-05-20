import hashlib
import hmac
import time
from datetime import datetime, timedelta, timezone

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import get_settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def create_access_token(subject: str) -> str:
    s = get_settings()
    expire = datetime.now(timezone.utc) + timedelta(minutes=s.jwt_expire_minutes)
    payload = {"sub": subject, "exp": expire}
    return jwt.encode(payload, s.jwt_secret, algorithm=s.jwt_algorithm)


def decode_access_token(token: str) -> str | None:
    s = get_settings()
    try:
        payload = jwt.decode(token, s.jwt_secret, algorithms=[s.jwt_algorithm])
        sub = payload.get("sub")
        if sub is None or not isinstance(sub, str):
            return None
        return sub
    except JWTError:
        return None


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, password_hash: str) -> bool:
    return pwd_context.verify(plain_password, password_hash)


def _download_sig_payload(node_id: str, exp: int) -> bytes:
    return f"{node_id}:{exp}".encode("utf-8")


def create_download_signature(node_id: str, exp: int) -> str:
    secret = get_settings().jwt_secret.encode("utf-8")
    return hmac.new(secret, _download_sig_payload(node_id, exp), hashlib.sha256).hexdigest()


def verify_download_signature(node_id: str, exp: int, sig: str) -> bool:
    if exp < int(time.time()):
        return False
    expected = create_download_signature(node_id, exp)
    return hmac.compare_digest(expected, sig)
