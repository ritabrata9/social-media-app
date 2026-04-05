from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine
from app import models
from app.routers import post, user, auth, likes
import time
from sqlalchemy.exc import OperationalError



# creates all tables defined in models.py if they don't already exist
# equivalent to running the CREATE TABLE sql manually in the raw version
for _ in range(10):
    try:
        models.Base.metadata.create_all(bind=engine)
        break
    except OperationalError:
        time.sleep(2)
        
app = FastAPI()

origins = ["*"]


app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/debug/db-confirm")
def confirm():
    result = db.execute("SELECT current_database();").fetchall()
    return {"db": result}

app.include_router(post.router)
app.include_router(user.router)
app.include_router(auth.router)
app.include_router(likes.router)

    
