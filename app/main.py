from typing import List
from fastapi import Body, Depends, FastAPI, Response, status, HTTPException
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from pydantic import BaseModel, StrictStr
from random import randrange

from app.utils import hash_password

from . import models, schemas
import json
import psycopg2
from psycopg2.extras import RealDictCursor
from app.database import SessionLocal, engine, get_db
from sqlalchemy.orm import Session

app = FastAPI()

# Create DB tables from the models we defined (if they don't exist)
# CAUTION: it does not let you modify tables, we need migrations (Alembic) for that
models.Base.metadata.create_all(bind=engine)

@app.get("/")
async def root():
    return {"message": "Welcome to my API"}

# GET ALL POSTS
@app.get("/posts", response_model=List[schemas.PostResponse])
async def get_posts(db: Session = Depends(get_db)):
    posts = db.query(models.Post).all()
    return posts  
    # FASTAPI automatically serializes posts into JSON
    # return JSONResponse(content=jsonable_encoder(posts))

# GET A POST
@app.get("/posts/{id}", response_model=schemas.PostResponse)
async def get_post(id: int, db: Session = Depends(get_db)): #___________ id: int means that `id` has to be an integer and it is going to try to convert the `id` to an int every time
    post = db.query(models.Post).filter(models.Post.id==id).first()
    if not post:
        # response.status_code = status.HTTP_404_NOT_FOUND
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"post with id: {id} not found"
        )
    return post

# CREATE A POST
@app.post("/posts", status_code=status.HTTP_201_CREATED, response_model=schemas.PostResponse) # ________ with status_code we are changing the default response
# async def create_posts(payload: dict = Body(...)):
async def create_posts(post: schemas.PostCreate, db: Session = Depends(get_db)):
    # create new ost object
    new_post = models.Post(**post.model_dump())
    # add post to DB
    db.add(new_post)
    # commit post to DB
    db.commit()
    # retrieve the post we created and store it back into the variable new_post
    db.refresh(new_post)
    return new_post

# DELETE A POST
@app.delete("/posts/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(id: int, db: Session = Depends(get_db)):
    post_query = db.query(models.Post).filter(models.Post.id==id)
    # check models.Post object
    if post_query.first() is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id: {id} not found"
        )
    post_query.delete(synchronize_session=False)
    db.commit()
    return
    # return Response(status_code=status.HTTP_204_NO_CONTENT) 
    # we deleted the post, we should not send any data back fast api throws an error
    # if we return the id of the post or something more

# UPDATE A POST
@app.put("/posts/{id}", status_code=status.HTTP_200_OK, response_model=schemas.PostResponse)
def update_post(id: int, post: schemas.PostCreate, db: Session = Depends(get_db)):
    post_query = db.query(models.Post).filter(models.Post.id==id)
    post_to_be_updated = post_query.first()
    if post_to_be_updated is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"post with id: {id} not found"
        )
    post_query.update(post.model_dump(), synchronize_session=False)
    db.commit()
    return post_to_be_updated # equals to return JSONResponse(content=jsonable_encoder(payload_dict))

# CREATE USER
@app.post("/users", status_code=status.HTTP_201_CREATED, response_model=schemas.UserResponse)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):

    # hash the password - user.password
    hashed_password = hash_password(user.password)
    # replace the plain text password in user
    user.password = hashed_password

    new_user = models.User(**user.model_dump())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user

@app.get("/users/{id}", response_model=schemas.UserResponse)
def get_user(id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == id).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"user with id: {id} not found"
        )
    return user