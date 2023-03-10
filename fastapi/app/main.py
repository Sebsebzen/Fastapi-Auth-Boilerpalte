from dotenv import find_dotenv, load_dotenv
load_dotenv(find_dotenv())

from datetime import datetime, timedelta
from fastapi import Depends, FastAPI, HTTPException, status, Response, Query
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
import logging
import yaml

from sqlalchemy.orm import Session
from typing import List, Optional

from . import auth, crud, models, schemas, sendmail
from .database import get_db, DBContext
from .logging import config_str


app = FastAPI()

# Logging
logging_config = yaml.safe_load(config_str)
logging.config.dictConfig(logging_config)

# CORS
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get('/', response_class=RedirectResponse, include_in_schema=False)
def docs():
    return RedirectResponse(url='/docs')


@app.post("/register")
def register_user(user: schemas.UserRegister, db: Session = Depends(get_db)):
    # check if email already exists
    db_user = crud.get_user_by_email(db=db, email=user.email)
    if db_user:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Email already registered")
    
    # check if username already exists
    db_user = crud.get_user_by_username(db=db, username=user.username)
    if db_user:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Username already registered")

    # create verification token
    pin = auth.create_pin()
    subject = {"username": user.username, "pin": pin}
    token = auth.verification_security.create_access_token(subject=subject)
    # create new user
    db_user = crud.create_user(db=db, user=user, token=token)

    # send email
    sendmail.send_mail(to=db_user.email, token=token, username=db_user.username, pin=pin)
    return {
        "message": "Register successful, please check your email to activate your account",
        }


@app.post('/login_token', response_model=schemas.Token)
def login_user_with_bearer_token(
    form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):
    db_user = crud.get_user_by_username(db=db, username=form_data.username)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Login information not correct"
        )

    if auth.verify_password(form_data.password, db_user.hashed_password):
        subject = {
            "username": db_user.username, 
            "role": db_user.role.value,
            "is_active": db_user.is_active,
            "email": db_user.email,
            }

        # Create new access/refresh tokens pair
        access_token = auth.access_security.create_access_token(subject=subject)
        refresh_token = auth.refresh_security.create_refresh_token(subject=subject)
        return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}      
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Login information not correct")


@app.post('/login_cookie')
def login_user_with_cookie(
    response: Response, form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):
    db_user = crud.get_user_by_username(db=db, username=form_data.username)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Login information not correct"
        )

    if auth.verify_password(form_data.password, db_user.hashed_password):
        subject = {
            "username": db_user.username, 
            "role": db_user.role.value,
            "is_active": db_user.is_active,
            "email": db_user.email,
            }

        # Create new access/refresh tokens pair
        access_token = auth.access_security.create_access_token(subject=subject)
        refresh_token = auth.refresh_security.create_refresh_token(subject=subject)

        # Create access/refresh cookies
        auth.access_security.set_access_cookie(response, access_token)
        auth.refresh_security.set_refresh_cookie(response, refresh_token)
        return {"message": "Logged in successfully"}
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Login information not correct")


@app.post("/logout")
def logout_and_unset_cookie(response: Response):
    auth.access_security.unset_access_cookie(response)
    auth.refresh_security.unset_refresh_cookie(response)
    return {"message": "Logged out successfully"}


@app.post("/refresh", response_model=schemas.Token)
def refresh_bearer_token(credentials = Depends(auth.get_credentials_refresh)):
    # Update access/refresh tokens pair
    access_token = auth.access_security.create_access_token(subject=credentials.subject)
    refresh_token = auth.refresh_security.create_refresh_token(subject=credentials.subject)
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}


@app.post("/refresh_cookie")
def refresh_cookie(response: Response, credentials = Depends(auth.get_credentials_refresh)):
    # Update access/refresh tokens pair
    access_token = auth.access_security.create_access_token(subject=credentials.subject)
    refresh_token = auth.refresh_security.create_refresh_token(subject=credentials.subject)

    # Create access/refresh cookies
    auth.access_security.set_access_cookie(response, access_token)
    auth.refresh_security.set_refresh_cookie(response, refresh_token)
    return {"message": "Cookies refreshed"}


@app.post("/resend_verification_email")
def resend_verification_email(username: str = Depends(auth.get_current_user), db: Session = Depends(get_db)):
    db_user = crud.get_user_by_username(db=db, username=username)
    if db_user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User already activated")

    # create new verification token
    pin = auth.create_pin()
    subject = {"username": db_user.username, "pin":pin}
    token = auth.verification_security.create_access_token(subject=subject)

    db_user.verification_token = token
    db.commit()

    # send email
    sendmail.send_mail(to=db_user.email, token=token, username=db_user.username, pin=pin)
    return {
        "message": "Please check your email to activate your account"
        }


@app.get("/verify/{token}", response_class=HTMLResponse)
def verify_user_with_link(token: str, db: Session = Depends(get_db)):
    # Decode verification token
    credentials = auth.verification_security._decode(token)
    if not credentials:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token or token expired") 
    
    db_user = crud.get_user_by_username(db, credentials['subject']['username'])

    if db_user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User already activated")

    db_user.is_active = True
    db.commit()
    return f"""
    <html>
        <head>
            <title>Registration confirmed</title>
        </head>
        <body>
            <h2>Successfully activated {db_user.username}!</h2>
            <a href="https://test.com">
                return
            </a>
        </body>
    </html>
    """


@app.post("/verify")
def verify_current_user_with_pin(pin: str = Query(min_length=4, max_length=4), db: Session = Depends(get_db), username: str = Depends(auth.get_current_user)):
    db_user = crud.get_user_by_username(db=db, username=username)
    if db_user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User already activated")

    verification = auth.verification_security._decode(db_user.verification_token)
    if not verification:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid pin or pin expired")

    if pin != verification['subject']["pin"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid pin")

    db_user.is_active = True
    db.commit()
    return f"""
    <html>
        <head>
            <title>Registration confirmed</title>
        </head>
        <body>
            <h2>Successfully activated {db_user.username}!</h2>
            <a href="https://test.com">
                return
            </a>
        </body>
    </html>
    """


@app.get("/user/me", response_model=schemas.UserPlain)
def get_current_user(db: Session = Depends(get_db), username: str = Depends(auth.get_current_user)):
    db_user = crud.get_user_by_username(db=db, username=username)
    return db_user

@app.get("/users", dependencies=[Depends(auth.check_active)], response_model=List[Optional[schemas.UserPlain]])
def get_all_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users = crud.get_users(db=db, skip=skip, limit=limit)
    return users

@app.get("/users/{user_id}", dependencies=[Depends(auth.check_active)], response_model=schemas.UserPlain)
def get_user_by_id(user_id: str, db: Session = Depends(get_db)):
    db_user = crud.get_user(db, id=user_id)
    if db_user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return db_user

@app.get("/adminsonly", dependencies=[Depends(auth.check_admin)], response_model=List[Optional[schemas.UserDB]])
def get_all_users_details(db: Session = Depends(get_db)):
    users = crud.get_users(db=db)
    return users
