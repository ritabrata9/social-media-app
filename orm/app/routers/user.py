from sqlalchemy.orm import Session
from app.database import get_db
from app import models
from app.schemas import UserCreate, UserOut
from app.utils import hash_password
from fastapi import HTTPException, Depends, APIRouter

router = APIRouter(
    prefix = "/users",
    tags = ['Users']
)

@router.post("/", status_code=201, response_model = UserOut)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    
    #hash the password    
    user.password = hash_password(user.password)

    new_user = models.User(**user.model_dump())
    db.add(new_user)      
    db.commit()           
    db.refresh(new_user) 
    return new_user

# GET /users/{id} — returns a single user info by id
@router.get("/{id}", response_model = UserOut)
def get_post(id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == id).first()  # SELECT * FROM users WHERE id = %s
    if not user:
        raise HTTPException(status_code=404, detail=f"User with id {id} not found")
    return user