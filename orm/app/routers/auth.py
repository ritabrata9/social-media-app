from fastapi import APIRouter, Depends, status, HTTPException, Response
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.schemas import UserLogin
from app.database import get_db
from app.utils import hash_password
from app import models, oauth2
from app.utils import verify_pwd


router = APIRouter(
    tags = ['Authentication']
)

@router.post('/login')
def login(user_credentials: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):

    user = db.query(models.User).filter(models.User.email == user_credentials.username).first()

    if not user:
        raise HTTPException(status_code=404, detail = f"Invalid credentials")
    
    if not verify_pwd(user_credentials.password, user.password):
        raise HTTPException(status_code=404, detail = f"Invalid credentials")
    
    #create a token

    access_token = oauth2.create_access_token(data = {"user_id": user.id})
    

    return {"access_token": access_token, "token_type": "bearer"}





