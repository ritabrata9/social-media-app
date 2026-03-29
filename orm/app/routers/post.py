from sqlalchemy.orm import Session
from app.database import get_db
from app import models, oauth2
from app.schemas import PostCreate, PostResponse
from typing import List, Optional
from fastapi import HTTPException, Depends, APIRouter

from app.utilities.moderation import is_disallowed

router = APIRouter(
    prefix="/posts",
    tags=['Posts']
)


#! GET /posts — returns all posts of a particular user
# Depends(get_db) injects a fresh database session for this request
# List[PostResponse] tells FastAPI to serialize each result using PostResponse
@router.get("/", response_model=List[PostResponse])
def get_posts(db: Session = Depends(get_db), limit: int = 10, search: Optional[str] = ""):

    posts = db.query(models.Post).filter(models.Post.title.contains(search)).limit(limit).all()
    return posts


#! POST /posts — CREATES a new post from the request body
# status 201 = Created
@router.post("/", status_code=201, response_model=PostResponse)
def create_post(
    post: PostCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(oauth2.get_current_user)
):
    # unpack the Pydantic model into the SQLAlchemy model using **post.model_dump()
    # equivalent to: Post(title=post.title, content=post.content, published=post.published)

    text = f"{post.title} {post.content}"

    if is_disallowed(text):
        raise HTTPException(
            status_code=403,
            detail="Post rejected: Disrespect towards the Supreme Leader is not allowed."
        )

    new_post = models.Post(
        **post.model_dump(),
        user_id=current_user.id
    )

    db.add(new_post)      # stage the insert
    db.commit()           # write to the database
    db.refresh(new_post)  # fetch the saved row back (needed to get the auto-generated id and created_at)

    return new_post


#! PUT /posts/{id} — overwrites all fields of an existing post
@router.put("/{id}", response_model=PostResponse)
def update_post(
    id: int,
    post: PostCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(oauth2.get_current_user)
):
    query = db.query(models.Post).filter(models.Post.id == id)
    existing_post = query.first()

    if not existing_post:  # check if the row exists before updating
        raise HTTPException(status_code=404, detail=f"Post with id {id} not found")

    if existing_post.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorised")

    # moderation check on updated content
    text = f"{post.title} {post.content}"

    if is_disallowed(text):
        raise HTTPException(
            status_code=403,
            detail="Update rejected: Disrespect towards supreme leader is not allowed."
        )

    query.update(post.model_dump(), synchronize_session=False)  # UPDATE posts SET ... WHERE id = %s
    db.commit()

    return query.first()  # return the updated row


#! DELETE /posts/{id} — deletes a post by id
# status 204 = No Content — success with no response body
@router.delete("/{id}", status_code=204)
def delete_post(
    id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(oauth2.get_current_user)
):

    query = db.query(models.Post).filter(models.Post.id == id)

    post = query.first()
    if post is None:
        raise HTTPException(status_code=404, detail=f"Post with id {id} not found")

    if post.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorised")

    query.delete(synchronize_session=False)  # DELETE FROM posts WHERE id = %s
    db.commit()