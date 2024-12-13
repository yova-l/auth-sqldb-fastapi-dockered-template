from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from datetime import timedelta
from jose import JWTError, jwt

from .model.base_auth import Authenticator, TokenData, Token
from .model.myusers_n_db_manager import UserInDB, User
from .model.myprocessor import PersonalizedWriteRequest, MyProcessor

app = FastAPI()
authenticator = Authenticator()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")
my_processor = MyProcessor()

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credential_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                        detail="Could not validate credentials", headers={"WWW-Authenticate": "Bearer"})
    try:
        payload = jwt.decode(token, authenticator.SECRET_KEY, algorithms=[authenticator.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credential_exception

        token_data = TokenData(username=username)
    except JWTError:
        raise credential_exception

    user = authenticator.get_user(username=token_data.username)
    if user is None:
        raise credential_exception

    return user


async def get_current_active_user(current_user: UserInDB = Depends(get_current_user)):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")

    return current_user


@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticator.authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Incorrect username or password", headers={"WWW-Authenticate": "Bearer"})
    access_token_expires = timedelta(minutes=authenticator.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = authenticator.create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires)
    return {"access_token": access_token, "token_type": "bearer"}

# ================== Your endpoints ==================

@app.post("/authreq/{pageid}") 
def write(pageid: str, message: PersonalizedWriteRequest, current_user: User = Depends(get_current_active_user)):
    # This is a simple example of how you can use the current_user object to check if the user has access to the pageid,
    # You must modify this function and the objects to fit your needs otherwise it will raise an exception
    if (not pageid in current_user.permitted_pages) or current_user.disabled:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="The page you attempted to write to either doesn't exist or you don't have access",
            headers={"WWW-Authenticate": "Bearer"}
            )
    my_processor.process(message.msg, pageid, current_user.username)
    return {"status": "Sucess", "detail": f"You are authorized to make somthing here: '{pageid}' and to use the message:'{message.msg}' to do whatever you want with that", "user_details_complete": current_user}

@app.get("/noauthreq")
def read(another_message: PersonalizedWriteRequest):
    return {"status": "Sucess", "detail": f"You don't need to be authorized to make somthing here and to use the message:'{another_message.msg}' to do whatever you want with that, this is a public endpoint"}