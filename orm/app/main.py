from fastapi import FastAPI
from app.database import engine
from app import models
from app.routers import post, user, auth



# creates all tables defined in models.py if they don't already exist
# equivalent to running the CREATE TABLE sql manually in the raw version
models.Base.metadata.create_all(bind=engine)

app = FastAPI()


app.include_router(post.router)
app.include_router(user.router)
app.include_router(auth.router)

    
