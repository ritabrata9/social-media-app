from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional

# PostCreate validates the incoming request body for create and update routes
# FastAPI runs this validation automatically before your route function executes
class PostCreate(BaseModel):
    title: str
    content: str
    published: bool = True  # optional field, defaults to True if not provided


# PostResponse defines the shape of data returned to the client
# having a separate response schema lets you control exactly what gets exposed
class PostResponse(BaseModel):
    id: int
    title: str
    content: str
    published: bool
    created_at: datetime  # included since it's set by postgres automatically on insert
    user_id: int

    # tells Pydantic to read data from SQLAlchemy model attributes
    # without this, Pydantic wouldn't know how to parse an ORM object
    class Config:
        from_attributes = True
    
class UserCreate(BaseModel):
    email: EmailStr
    password: str

class UserOut(BaseModel):
    id:int
    email:EmailStr

    class Config:
        from_attributes = True

class UserLogin(BaseModel):
    email:EmailStr
    password:str


class Token(BaseModel):
    access_token : str
    token_type : str

class TokenData(BaseModel):
    id : Optional[int] = None