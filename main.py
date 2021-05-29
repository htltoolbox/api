#
# HTL-Toolbox /main.py
#
# This file contains most of the API-Performable functions

# Import External Dependencies

# Import Standard Libs

import uuid
from datetime import timedelta

# Import Dependencies

import uvicorn
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from pydantic import ValidationError
from starlette.responses import JSONResponse, RedirectResponse

# Import Local Functions and Models

from assets.database import datasource
from assets.filter import htmlspecialchars
from functions.app import getApp
from functions.clickboard import get_all_clickboards, create_clickboard
from functions.hashing import get_current_active_user, authenticate_user, get_password_hash
from functions.sessionkey import create_access_token
from functions.user import create_user, get_user, is_teacher, get_all_users, remove_passwordhash_obj, push_data
from models.apikey import ApiKey
from models.clickboard import Clickboard, TempClickboard
from models.mail import Mail
from models.token import Token
from models.user import User, preUser

# Initialize FastAPI

app = FastAPI(title="HTL-TOOLBOX-API", version="0.0.3-Alpha-1")

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*']
)


@app.get("/")
async def main():
    return {"message": "Hello World"}


# Post

@app.post("/token", response_model=Token)
async def login_for_access_token(ip: str, form_data: OAuth2PasswordRequestForm = Depends()):
    # Call Authenticate User Function from the Formdata

    account = authenticate_user(form_data.username, form_data.password, ip)

    # Check account otherwise return 401

    if not account:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Create Access-Token ans set valid-timespan to 4-weeks

    access_token_expires = timedelta(weeks=4)
    access_token = create_access_token(
        data={"sub": account.EMAIL}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@app.post("/flow/oauth2/temphash/{appid}")
async def flow_oauth2_temphash(appid: int, form_data: OAuth2PasswordRequestForm = Depends()):
    account = authenticate_user(form_data.username, form_data.password)
    if not account:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    account.TEMPHASH = uuid.uuid1().hex
    push_data(account)
    APP = getApp(ID=appid)
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "redirect-url": APP.REDIR_URL,
            "temphash": account.TEMPHASH,
        }
    )


@app.post("/flow/oauth2/authapp/{temphash}", response_model=Token)
async def flow_oauth2_authapp(temphash: str, apikey: str):
    try:
        await getApp(API_KEY=apikey)
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            detail="API_KEY was rejected. Please Provide a Valid one."
        )
    account = get_user(TEMPHASH=temphash)
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


# Mail API POST

@app.post("/sendmail")
async def api_send_mail(apikey: str, mail: Mail):
    # This creation of the API-Key object will throw an error if the key is not valid

    apikey = ApiKey(APIKEY=apikey)

    # Try catch block to avoid the posibily of the object not beeing created

    try:

        if apikey.PERMISSION >= 2:

            if mail.send():
                return JSONResponse(
                    status_code=status.HTTP_200_OK,
                    content="E-Mail was sent successfully"
                )
            else:
                return HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Internal Server Error with Processing the Mail"
                )
        else:
            return HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not allowed to send Mails"
            )

    # Catch ValidationError if apikey is not valid

    except ValidationError as e:
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content=e.errors()
        )


# User GET Operrations


@app.get("/users/me", response_model=User, description="shows the current active logged in user")
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    return remove_passwordhash_obj(current_user)


@app.get("/users/{id}", response_model=User)
async def read_user_by_id(user_id: int, current_user: User = Depends(get_current_active_user)):
    if current_user.PERMISSION_LEVEL >= 3:
        return await get_user(ID=user_id)
    else:
        return JSONResponse(status_code=status.HTTP_403_FORBIDDEN,
                            content="Not sufficient Permissions to view other users")


@app.get("/users", description="returns all users (for admin dashboard)")
async def return_all_users(current_user: User = Depends(get_current_active_user)):
    if current_user.PERMISSION_LEVEL >= 3:
        try:
            return await get_all_users()
        except ValidationError as e:
            return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content=e.errors())
    else:
        return JSONResponse(status_code=status.HTTP_403_FORBIDDEN,
                            content="Not sufficient Permissions to view other users")


# Put

@app.put("/admin/create/user", description="Operation for Admins to manually create a user through the API")
async def admin_create_user(user: User, current_user: User = Depends(get_current_active_user)):
    # Check if the logged-in-User hat Admin Priveleges

    if current_user.PERMISSION_LEVEL >= 3:
        user.PASSWORD_HASH = get_password_hash(user.PASSWORD_HASH)
        create_user(user)
        return JSONResponse(status_code=status.HTTP_201_CREATED, content="User was successfully created")
    else:
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content="Not sufficient Permissions to create other users"
        )


@app.put("/create/user")
async def form_create_user(api_key: str, user: preUser):
    try:
        ApiKey(APIKEY=api_key)
    except ValidationError as e:
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content=e.errors()
        )

    ds = datasource()
    ds.connect()

    SQL = "SELECT EMAIL FROM USERDATA WHERE EMAIL = %s"
    PAR = (user.EMAIL,)

    ds.execute(SQL, PAR)
    data = ds.fetch_row()

    ds.close()

    if data is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User is already registered"
        )

    PERMISSION_LEVEL = 0

    isTeacher = is_teacher(user.EMAIL)

    # Check if User is in the Global Teacher Database
    if isTeacher:
        PERMISSION_LEVEL = 1
        user.CLASS = "LEHRER"
    elif user.CLASS == "LEHRER":
        raise HTTPException(
            status_code=status.HTTP_417_EXPECTATION_FAILED,
            detail="User is not a teacher"
        )

    NAME = user.EMAIL.split(".")[0].capitalize()
    LASTNAME = user.EMAIL.split(".")[1].split("@")[0].capitalize()

    if LASTNAME[-2:].isdigit():
        LASTNAME = LASTNAME[:-2]

    try:
        account = User(
            EMAIL=user.EMAIL,
            PASSWORD_HASH=get_password_hash(user.PASSWORD),
            NAME=NAME,
            LASTNAME=LASTNAME,
            CLASS=user.CLASS,
            PERMISSION_LEVEL=PERMISSION_LEVEL,
            ACTIVE=False
        )
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=e.errors()
        )
    create_user(account)

    mail = Mail(
        to=user.EMAIL,
        subject="Account Aktivieren",
        message="https://api.toolbox.philsoft.at/account/activate/" + account.TEMPHASH,
        html=False
    )

    if mail.send():
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content="User successfully created"
        )
    else:
        return HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="There was some error with the mail processing"
        )

    # Clickboards


@app.get("/v1/apps/clickboards", response_model_include=Clickboard)
async def all_clickboards():
    return get_all_clickboards()


@app.put("/v1/apps/clickboards/create")
async def api_create_clickboard(click: TempClickboard, current_user: User = Depends(get_current_active_user)):
    if current_user.PERMISSION_LEVEL >= 1:
        create_clickboard(click)
        return JSONResponse(
            status_code=status.HTTP_201_CREATED,
            content="Clickboard created"
        )
    else:
        return JSONResponse(status_code=status.HTTP_403_FORBIDDEN,
                            content="Not sufficient Permissions to view other users")


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
