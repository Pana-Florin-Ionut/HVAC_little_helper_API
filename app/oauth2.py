from jose import JWTError, jwt
from dotenv import load_dotenv
import os
from . import schemas
from datetime import datetime, timedelta
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer


load_dotenv()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

secret_key = os.getenv("SECRET_KEY")
algorithm = os.getenv("ALGORITHM")
expiration_time = os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES")


def create_access_token(data: dict):
    print(data)
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=int(expiration_time))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, secret_key, algorithm=algorithm)
    return encoded_jwt


def verify_access_token(token: str, credentials_exception):
    try:
        payload = jwt.decode(token, secret_key, algorithms=[algorithm])
        print(payload)
        id: str = payload.get("user_id")
        company_id: str = payload.get("company_id")
        role: str = payload.get("role")
        if id is None:
            raise credentials_exception
        # token_data = schemas.TokenData(id=id)  # can add other data to the token
        token_data = schemas.TokenData(id=id, company_id=company_id, role=role)

        return token_data
    except JWTError:
        raise credentials_exception


def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=f"Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    return verify_access_token(token, credentials_exception)
