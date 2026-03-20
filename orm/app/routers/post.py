from sqlalchemy.orm import Session
from app.database import get_db
from app import models, oauth2
from app.schemas import PostCreate, PostResponse
from typing import List
from fastapi import HTTPException, Depends, APIRouter

router = APIRouter(
    prefix = "/posts",
    tags = ['Posts']
)

# GET /posts — returns all posts
# Depends(get_db) injects a fresh database session for this request
# List[PostResponse] tells FastAPI to serialize each result using PostResponse
@router.get("/", response_model=List[PostResponse])
def get_posts(db: Session = Depends(get_db)):
    posts = db.query(models.Post).all()  # SELECT * FROM posts
    return posts


# GET /posts/{id} — returns a single post by id
@router.get("/{id}", response_model=PostResponse)
def get_post(id: int, db: Session = Depends(get_db)):
    post = db.query(models.Post).filter(models.Post.id == id).first()  # SELECT * FROM posts WHERE id = %s
    if not post:
        raise HTTPException(status_code=404, detail=f"Post with id {id} not found")
    return post


# POST /posts — creates a new post from the request body
# status 201 = Created
@router.post("/", status_code=201, response_model=PostResponse)
def create_post(post: PostCreate, db: Session = Depends(get_db), get_current_user:int = Depends(oauth2.get_current_user)):
    # unpack the Pydantic model into the SQLAlchemy model using **post.model_dump()
    # equivalent to: Post(title=post.title, content=post.content, published=post.published)
    new_post = models.Post(**post.model_dump())
    db.add(new_post)      # stage the insert
    db.commit()           # write to the database
    db.refresh(new_post)  # fetch the saved row back (needed to get the auto-generated id and created_at)
    return new_post


# PUT /posts/{id} — overwrites all fields of an existing post
@router.put("/{id}", response_model=PostResponse)
def update_post(id: int, post: PostCreate, db: Session = Depends(get_db)):
    query = db.query(models.Post).filter(models.Post.id == id)
    if not query.first():  # check if the row exists before updating
        raise HTTPException(status_code=404, detail=f"Post with id {id} not found")
    query.update(post.model_dump(), synchronize_session=False)  # UPDATE posts SET ... WHERE id = %s
    db.commit()
    return query.first()  # return the updated row


# DELETE /posts/{id} — deletes a post by id
# status 204 = No Content — success with no response body
@router.delete("/{id}", status_code=204)
def delete_post(id: int, db: Session = Depends(get_db)):
    query = db.query(models.Post).filter(models.Post.id == id)
    if not query.first():
        raise HTTPException(status_code=404, detail=f"Post with id {id} not found")
    query.delete(synchronize_session=False)  # DELETE FROM posts WHERE id = %s
    db.commit()