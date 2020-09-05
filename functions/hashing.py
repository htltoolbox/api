from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import jwt, JWTError
from passlib.context import CryptContext
from starlette.status import HTTP_401_UNAUTHORIZED

from functions import user as u
import env as e
from functions.user import get_user
from models.tokendata import TokenData
from models.user import User

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

ALOGRITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def authenticate_user(EMAIL: str, PASSWORD: str):
    account = u.get_user(EMAIL=EMAIL)
    if not account:
        return False
    if not verify_password(PASSWORD, account.PASSWORD_HASH):
        return False
    return account


async def get_current_user(token: str = Depends(oauth2_scheme)):
    credential_email_none_exception = HTTPException(
        status_code=HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials [email none]",
        headers={"WWW-Authenticate": "Bearer"}
    )
    credential_jwt_exception = HTTPException(
        status_code=HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials [jwt]",
        headers={"WWW-Authenticate": "Bearer"}
    )
    credential_email_db_exception = HTTPException(
        status_code=HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials [email-db]",
        headers={"WWW-Authenticate": "Bearer"}
    )
    try:
        # dekodieren des JWT
        payload = jwt.decode(token, e.SECRET_KEY, algorithms=[ALOGRITHM])
        # get EMAIL out to the JWT package
        EMAIL: str = payload.get("sub")
        # check if field EMAIL is set
        if EMAIL is None:
            # if not raise credential exception
            raise credential_email_none_exception
        token_data = TokenData(EMAIL=EMAIL)
    except JWTError:
        raise credential_jwt_exception
    user = get_user(EMAIL=token_data.EMAIL)
    if user is None:
        raise credential_email_db_exception
    return user


async def get_current_active_user(current_user: User = Depends(get_current_user)):
    if not current_user.ACTIVE:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user
