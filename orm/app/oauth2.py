from jose import JWTError, jwt
from datetime import datetime, timedelta

# SECRET_KEY
# algo = hs256
# expiration time

# generate using command:= openssl rand -hex 32    (bash)
SECRET_KEY = "62bc94dd8c55da1738cfc40b8c32bffce6707d70ad5d680e7b42560cffa71380"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

def create_access_token(data: dict):
    to_encode = data.copy()
    
    expire = datetime.now() + timedelta(minutes = ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    return encoded_jwt

