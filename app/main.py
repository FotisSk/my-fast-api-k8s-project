from typing import Optional
from fastapi import Body, Depends, FastAPI, Response, status, HTTPException
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from pydantic import BaseModel, StrictStr
from random import randrange
from . import models, schemas
import json
import psycopg2
from psycopg2.extras import RealDictCursor
from app.database import SessionLocal, engine, get_db
from sqlalchemy.orm import Session

from app.database import DatabaseHandler

app = FastAPI()

# create DB tables from the models we defined (if they don't exist)
# ! it does not let you modify tables, we need migrations (Alembic) for that !
models.Base.metadata.create_all(bind=engine)

# Database Connection using psycopg2
handler = DatabaseHandler()
conn = handler.get_connection() 
cursor = conn.cursor()
print("Database connection was successful")

my_posts = [
    {   
        "id": 1,
        "title": "title of post 1",
        "content": "content of post 1"
    },
    {
        "id": 2,
        "title": "favorite foods",
        "content": "I like pizza"
    }
]

def find_post(id: int):
    """
    - We create a generator object using () instead of [] 
    - Every generator is an iterator, not the other way around.
    - We apply next(iterator_obj, default_value) on it (None if nothing is found).
    - Every iterator has to have __next__() and __iter__() implemented.
    - List is an iterable that has __iter()__ implemented. -> that's why iter(list_object) results in an iterator
    - We use an iterator if we want to traverse a list just once and do nothing more with it.
    """
    return next((post for post in my_posts if post["id"] == id), None)

def find_index(id: int):
    for i, post in enumerate(my_posts):
        if post["id"] == id:
            return i

@app.get("/")
async def root():
    return {"message": "Welcome to my API"}

# GET all
@app.get("/posts")
async def get_posts(db: Session = Depends(get_db)):
    # cursor.execute("""SELECT * FROM posts""")
    # posts = cursor.fetchall()
    posts = db.query(models.Post).all()
    return {"data": posts}  # FASTAPI automatically serializes my_posts into JSON
    # return JSONResponse(content=jsonable_encoder(posts))

# GET one
@app.get("/posts/{id}")
async def get_post(id: int, db: Session = Depends(get_db)): #, response: Response):   #___________ id: int means that `id` has to be an integer and it is going to try to convert the `id` to an int every time
    # post = find_post(id)
    # cursor.execute("""SELECT * FROM posts WHERE id = %s""", (str(id),))
    # post = cursor.fetchone()
    post = db.query(models.Post).filter(models.Post.id==id).first()
    if not post:
        # response.status_code = status.HTTP_404_NOT_FOUND
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"post with id: {id} not found"
        )
    return {"data": post}

# CREATE
@app.post("/posts", status_code=status.HTTP_201_CREATED) # ________ with status_code we are changing the default response
# async def create_posts(payload: dict = Body(...)):
async def create_posts(post: schemas.PostCreate, db: Session = Depends(get_db)):
    # cursor.execute(
    #     """INSERT INTO posts (title, content, published) VALUES (%s, %s, %s) RETURNING *""",
    #     (post.title, post.content, post.published)
    # )
    # new_post = cursor.fetchone()
    # conn.commit()

    # create new ost object
    new_post = models.Post(**post.model_dump())
    # add post to DB
    db.add(new_post)
    # commit post to DB
    db.commit()
    # retrieve the post we created and store it back into the variable new_post
    db.refresh(new_post)    # 
    return {"data": new_post}                           #_________________________________ send the newly created post back to the Front End

# DELETE
@app.delete("/posts/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(id: int, db: Session = Depends(get_db)):
    # index = find_index(id)
    # cursor.execute("""DELETE FROM posts WHERE id=%s RETURNING *""", (str(id),))
    # deleted_post = cursor.fetchone()

    # return the sqlalchemy.orm.query.Query object
    post_query = db.query(models.Post).filter(models.Post.id==id)
    # check models.Post object
    if post_query.first() is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id: {id} not found"
        )
    # conn.commit()
    post_query.delete(synchronize_session=False)
    db.commit()
    return
    # return Response(status_code=status.HTTP_204_NO_CONTENT) # ______ we deleted the post, we should not send any data back fast api throws an arror if we return the id of the post or something more

# UPDATE
@app.put("/posts/{id}", status_code=status.HTTP_200_OK)
def update_post(id: int, post: schemas.PostCreate, db: Session = Depends(get_db)):
    # index = find_index(id)
    # payload_dict = payload.model_dump()
    # cursor.execute(
    #     """UPDATE products SET title=%s, content=%s, published=%s WHERE id=%s RETURNING *""",
    #     (post.title, post.content, post.published, str(id))
    # )
    # updated_post = cursor.fetchone()
    post_query = db.query(models.Post).filter(models.Post.id==id)
    post_to_be_updated = post_query.first()
    if post_to_be_updated is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"post with id: {id} not found"
        )
    post_query.update(post.model_dump(), synchronize_session=False)
    db.commit()
    # conn.commit()
    return {"data": post_to_be_updated} # equals to return JSONResponse(content=jsonable_encoder(payload_dict))
