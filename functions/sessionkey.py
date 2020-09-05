from datetime import timedelta, datetime
from typing import Optional
from jose import jwt

import env as e
import functions.hashing as hash


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(weeks=4)
    to_encode.update({"exp": expire})
    encode_jwt = jwt.encode(to_encode, e.SECRET_KEY, algorithm=hash.ALOGRITHM)
    return encode_jwt
