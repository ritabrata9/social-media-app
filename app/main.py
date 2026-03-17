from fastapi import FastAPI, HTTPException
from app.database import cursor, conn
from app.schemas import PostCreate

app = FastAPI()


@app.get("/posts")
def get_posts():
    cursor.execute("SELECT * FROM posts")
    posts = cursor.fetchall()
    return {"data": posts}


@app.get("/posts/{id}")
def get_post(id: int):
    cursor.execute("SELECT * FROM posts WHERE id = %s", (id,))
    post = cursor.fetchone()
    if not post:
        raise HTTPException(status_code=404, detail=f"Post with id {id} not found")
    return {"data": post}


@app.post("/posts", status_code=201)
def create_post(post: PostCreate):
    cursor.execute(
        "INSERT INTO posts (title, content, published) VALUES (%s, %s, %s) RETURNING *",
        (post.title, post.content, post.published)
    )
    new_post = cursor.fetchone()
    conn.commit()
    return {"data": new_post}


@app.put("/posts/{id}")
def update_post(id: int, post: PostCreate):
    cursor.execute(
        "UPDATE posts SET title = %s, content = %s, published = %s WHERE id = %s RETURNING *",
        (post.title, post.content, post.published, id)
    )
    updated_post = cursor.fetchone()
    if not updated_post:
        raise HTTPException(status_code=404, detail=f"Post with id {id} not found")
    conn.commit()
    return {"data": updated_post}


@app.delete("/posts/{id}", status_code=204)
def delete_post(id: int):
    cursor.execute("DELETE FROM posts WHERE id = %s RETURNING *", (id,))
    deleted_post = cursor.fetchone()
    if not deleted_post:
        raise HTTPException(status_code=404, detail=f"Post with id {id} not found")
    conn.commit()