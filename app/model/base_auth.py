from passlib.context import CryptContext
from pydantic import BaseModel
from datetime import datetime, timedelta, timezone
from jose import jwt
from dotenv import load_dotenv
import os

from .myusers_n_db_manager import SqlDbManager
from .myusers_n_db_manager import process_user


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None


class Authenticator:
    # Whaever defined here
    # Belongs to the class (Authenticator.auth_scheme is valid as vell as auth_instance.auth_scheme)
    def __init__(self):
        # Belongs to the instance
        load_dotenv()
        self.pswd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        self.ACCESS_TOKEN_EXPIRE_MINUTES = 30
        self.SECRET_KEY = os.getenv("secret_key") # to generate it use openssl rand -hex 32
        self.ALGORITHM = os.getenv("algorithm")
        self.db_manager = SqlDbManager()
        self._process_user = process_user


    def verify_password(self, plain_password, hashed_password):
        return self.pswd_context.verify(plain_password, hashed_password)


    def get_password_hash(self, password):
        return self.pswd_context.hash(password)


    def get_user(self, username: str):
        #Consults the DB
        res = self.db_manager.get_user(username=username)
        if res:
            return self._process_user(res)


    def authenticate_user(self, username: str, password: str):
        user = self.get_user(username)
        if not user:
            return False
        if not self.verify_password(password, user.hashed_password):
            return False
        return user


    def create_access_token(self, data: dict, expires_delta: timedelta | None = None):
        to_encode = data.copy() # To not affect the original
        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(timezone.utc) + timedelta(minutes=15)

        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)
        return encoded_jwt