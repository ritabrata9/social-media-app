from fastapi import FastAPI, HTTPException

# cursor — the object used to execute SQL queries against the database
# conn — the database session; needed to call conn.commit() to save any writes
from app.database import cursor, conn

# PostCreate is a Pydantic model — FastAPI uses it to automatically validate
# and parse the JSON request body before your function even runs
from app.schemas import PostCreate

# creates the FastAPI app instance — all routes are registered on this object
# uvicorn targets this when you run: uvicorn app.main:app
app = FastAPI()


# GET /posts — returns every row in the posts table
@app.get("/posts")
def get_posts():
    cursor.execute("SELECT * FROM posts")
    posts = cursor.fetchall()  # list of dicts; empty list [] if no posts exist
    return {"data": posts}


# GET /posts/{id} — returns a single post matching the given id
# {id} in the path is a path parameter — FastAPI extracts it and casts it to int automatically
@app.get("/posts/{id}")
def get_post(id: int):
    # %s is a parameterized placeholder — psycopg2 substitutes the value safely
    # this prevents SQL injection (never use f-strings to build SQL queries)
    # (id,) must be a tuple — psycopg2 requires an iterable even for a single value
    cursor.execute("SELECT * FROM posts WHERE id = %s", (id,))
    post = cursor.fetchone()  # returns one dict, or None if no row matched
    if not post:
        # HTTPException aborts the request and sends a structured JSON error response
        # status 404 = Not Found
        raise HTTPException(status_code=404, detail=f"Post with id {id} not found")
    return {"data": post}


# POST /posts — inserts a new post using the JSON body from the request
# status_code=201 = "Created" — more semantically correct than the default 200 for insertions
@app.post("/posts", status_code=201)
def create_post(post: PostCreate):
    # post.title, post.content, post.published come from the validated request body
    # RETURNING * tells postgres to return the full inserted row — saves a second SELECT
    cursor.execute(
        "INSERT INTO posts (title, content, published) VALUES (%s, %s, %s) RETURNING *",
        (post.title, post.content, post.published)
    )
    new_post = cursor.fetchone()
    # writes are held in a transaction until commit() is called — nothing is saved without this
    conn.commit()
    return {"data": new_post}


# PUT /posts/{id} — overwrites all fields of an existing post
# reuses PostCreate schema since the required fields are the same as creation
@app.put("/posts/{id}")
def update_post(id: int, post: PostCreate):
    # RETURNING * returns the updated row — if it's None, no row matched the id
    cursor.execute(
        "UPDATE posts SET title = %s, content = %s, published = %s WHERE id = %s RETURNING *",
        (post.title, post.content, post.published, id)
    )
    updated_post = cursor.fetchone()  # None means the id didn't exist
    if not updated_post:
        raise HTTPException(status_code=404, detail=f"Post with id {id} not found")
    conn.commit()
    return {"data": updated_post}


# DELETE /posts/{id} — deletes the post with the given id
# status_code=204 = "No Content" — the standard success response for deletes (no body returned)
@app.delete("/posts/{id}", status_code=204)
def delete_post(id: int):
    # RETURNING * lets us check whether a row actually existed before deletion
    # without it we'd have no way to distinguish "deleted" from "never existed"
    cursor.execute("DELETE FROM posts WHERE id = %s RETURNING *", (id,))
    deleted_post = cursor.fetchone()
    if not deleted_post:
        raise HTTPException(status_code=404, detail=f"Post with id {id} not found")
    conn.commit()