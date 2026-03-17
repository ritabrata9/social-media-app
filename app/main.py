from fastapi import FastAPI
from app.database import cursor

app = FastAPI()

@app.get("/")
def test_db():
    cursor.execute("SELECT * FROM posts")
    posts = cursor.fetchall()
    return {"data": posts}