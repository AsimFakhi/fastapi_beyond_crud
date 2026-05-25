from passlib.context import CryptContext
import jwt
from typing import Any
from datetime import datetime, timedelta, timezone
import uuid
import logging
from src.config import CONF

password_cotext = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)

class TokenError(Exception):
    pass

class TokenExpiredError(TokenError):
    pass

class TokenInvalidError(TokenError):
    pass

def generate_password_hash(password:str) -> str:
    hashed_pw = password_cotext.hash(password)
    return hashed_pw

def verify_password(password: str, hashed_pw:str) -> bool:
    return password_cotext.verify(password, hashed_pw)

# ─── PAYLOAD BUILDER ───────────────────────────────────
def _build_payload(
        subject:str, user_data:dict[str, Any],
        expiry: timedelta, toke_type:str
)-> dict [str, Any]:
    now = datetime.now(timezone.utc)
    return {
        "sub": subject,
        "user": user_data,
        "expiry" : int((now + expiry).timestamp()),
        "issued_at": int(now.timestamp()),
        "jti" : str(uuid.uuid4()), # unique token id (for revocation)
        "token_type": toke_type,
        "audience": CONF.JWT_AUDIENCE,
        "issuer": CONF.JWT_ISSUER
    }

def _serialize_value(value):
    if isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, uuid.UUID):
        return str(value)
    
def _clean_palyload(payload:dict)->dict:
    return {k:_serialize_value(v) for k,v in payload.items()}


# ─── TOKEN CREATION ────────────────────────────────────
def create_access_token(user_data:dict[str, Any], expiry:timedelta | None=None)->str:
    expiry = expiry or timedelta(minutes=CONF.ACCESS_TOKEN_EXPIRY_MINUTES)
    payload = _build_payload(
        subject=str(user_data["uid"]),
        user_data=user_data,
        expiry=expiry,
        toke_type="access",
    )
    token = jwt.encode(
        payload=payload,
        key=CONF.JWT_SECRET,
        algorithm=CONF.JWT_ALGORITHM
        )
    return token

def create_refresh_token(user_data:dict[str, Any])->str:
    payload = _build_payload(
        subject=str(user_data["uid"]),
        user_data=user_data,
        expiry=timedelta(days=CONF.REFRESH_TOKEN_EXPIRY_DAYS),
        toke_type="refresh"
    )
    return jwt.encode(
        payload=payload,
        key=CONF.JWT_SECRET,
        algorithm=CONF.JWT_ALGORITHM
    )

# ─── TOKEN DECODE ──────────────────────────────────────
def decode_token(token:str)->dict[str, Any]:
    print(token)
    try:
        return jwt.decode(
            jwt=token,
            key=CONF.JWT_SECRET,
            algorithms=[CONF.JWT_ALGORITHM],
            # audience=CONF.JWT_AUDIENCE,
            # issuer=CONF.JWT_ISSUER,
            options={"require":["expiry","issued_at", "sub", "token_type"]}
        )
    except jwt.ExpiredSignatureError as e:
        raise TokenExpiredError("Token has expired.") from e
    except jwt.PyJWTError as e:
        raise TokenInvalidError("Token is invalid") from e
    except Exception as e:
        logging.exception(f"Unexpected error in token decode. => {e}")
        raise TokenInvalidError("Token decode failed.") from e
    