from datetime import timedelta
from typing import Optional

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import ValidationError
from starlette.responses import JSONResponse

from functions.hashing import get_current_active_user, authenticate_user, get_password_hash
from functions.sessionkey import create_access_token
from functions.user import create_user, get_user, is_teacher
from models.token import Token
from models.user import User
from models.apikey import ApiKey

app = FastAPI()


# Post


@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    account = authenticate_user(form_data.username, form_data.password)
    if not account:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(weeks=4)
    access_token = create_access_token(
        data={"sub": account.EMAIL}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


# User get Operrations


@app.get("/users/me", response_model=User, description="shows the current active logged in user")
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    return current_user


@app.get("/users/{id}", response_model=User)
async def read_user_by_id(id: int, current_user: User = Depends(get_current_active_user)):
    if current_user.PERMISSION_LEVEL >= 3:
        return get_user(ID=id)
    else:
        return JSONResponse(status_code=status.HTTP_403_FORBIDDEN,
                            content="Not sufficent Permissions to view other users")


# Put

@app.put("/admin/create/user")
async def admin_create_user(user: User, apikey: Optional[ApiKey] = None,
                            current_user: User = Depends(get_current_active_user)):
    if current_user.PERMISSION_LEVEL >= 3:
        user.PASSWORD_HASH = get_password_hash(user.PASSWORD_HASH)
        create_user(user)
        return JSONResponse(status_code=status.HTTP_201_CREATED, content="User was successfully created")
    else:
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content="Not sufficent Permissions to create other users"
        )


@app.put("/create/user")
async def form_create_user(api_key: str, u_email: str, u_password: str, u_class: str):
    try:
        ApiKey(APIKEY=api_key)
    except ValidationError as e:
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content=e.errors()
        )

    PERMISSION_LEVEL = 0
    if is_teacher(u_email):
        PERMISSION_LEVEL = 1

    NAME = u_email.split(".")[0].capitalize()
    LASTNAME = u_email.split(".")[1].split("@")[0].capitalize()

    if LASTNAME[:-2].isdigit():
        LASTNAME = LASTNAME[:-2]


    try:
        account = User(
            EMAIL=u_email,
            PASSWORD_HASH=get_password_hash(u_password),
            NAME=NAME,
            LASTNAME=LASTNAME,
            CLASS=u_class,
            PERMISSION_LEVEL=PERMISSION_LEVEL,
            ACTIVE=False
        )
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=e.errors()
        )
    create_user(account)
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content="User succesfully created"
    )
