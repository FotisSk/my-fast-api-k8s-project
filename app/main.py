from fastapi import FastAPI

from . import models
from app.database import engine
from app.routers import post, user

app = FastAPI()

app.include_router(post.router)
app.include_router(user.router)

# Create DB tables from the models we defined (if they don't exist)
# CAUTION: it does not let you modify tables, we need migrations (Alembic) for that
models.Base.metadata.create_all(bind=engine)

@app.get("/")
async def root():
    return {"message": "Welcome to my API"}
