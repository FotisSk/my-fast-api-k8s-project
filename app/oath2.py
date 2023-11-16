from fastapi import Depends, HTTPException , status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from datetime import datetime, timedelta

from app import models, schemas
from app.config import settings
from app.database import get_db

"""
We use the instance of OAuth2PasswordBearer as a dependency in your FastAPI
routes or dependencies. When a route or function has this dependency, FastAPI
automatically handles the extraction of the bearer token from the request.
"""
oath2_scheme = OAuth2PasswordBearer(tokenUrl="login")

SECRET_KEY = settings.secret_key
ALGORITHM = settings.algorithm
ACCESS_TOKEN_EXPIRE_MINUTES = settings.access_token_expire_minutes

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_access_token(token: str, credentials_exception):

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        id: str = payload.get("user_id")

        if id is None:
            raise credentials_exception
    
        # validate token_data with schema
        token_data = schemas.TokenData(id=str(id))
    except JWTError as e:
        raise credentials_exception
    return token_data
    
def get_current_user(token: str = Depends(oath2_scheme), db: Session = Depends(get_db)):
    """
    Use it as a dependency for endpoints that require the user 
    to be logged in.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"}
    )
    token_data = verify_access_token(token, credentials_exception)
    user = db.query(models.User).filter(models.User.id == token_data.id).first()
    return user