from typing import Optional
from fastapi import Body, FastAPI, Response, status, HTTPException
from pydantic import BaseModel, StrictStr
from random import randrange
import json
import psycopg2
from psycopg2.extras import RealDictCursor

from app.database import DatabaseHandler

app = FastAPI()

# Database Connection
handler = DatabaseHandler()
conn = handler.get_connection() 
cursor = conn.cursor()
print("Database connection was successful")

class Post(BaseModel):
    """
    Validator class to ensure data is received in an expected way
    from our `/createposts` endpoint.
    """
    title: str
    content: str
    published: bool = True # optional field with default value to our schema



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

@app.get("/posts")
async def get_posts():
    cursor.execute("""SELECT * FROM posts""")
    posts = cursor.fetchall()
    return {"data": posts}                             #_________________________________ FASTAPI automatically serializes my_posts into JSON

@app.get("/posts/{id}")
async def get_post(id: int): #, response: Response):   #___________ id: int means that `id` has to be an integer and it is going to try to convert the `id` to an int every time
    # post = find_post(id)
    cursor.execute("""SELECT * FROM posts WHERE id = %s""", (str(id),))
    post = cursor.fetchone()
    if not post:
        # response.status_code = status.HTTP_404_NOT_FOUND
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"post with id: {id} not found"
        )
    return {"data": post}

@app.post("/posts", status_code=status.HTTP_201_CREATED) # ________ with status_code we are changing the default response
# async def create_posts(payload: dict = Body(...)):
async def create_posts(post: Post):
    cursor.execute(
        """INSERT INTO posts (title, content, published) VALUES (%s, %s, %s) RETURNING *""",
        (post.title, post.content, post.published)
    )
    new_post = cursor.fetchone()
    conn.commit()
    return {"data": new_post}                           #_________________________________ send the newly created post back to the Front End

@app.delete("/posts/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(id: int):
    # index = find_index(id)
    cursor.execute("""DELETE FROM posts WHERE id=%s RETURNING *""", (str(id),))
    deleted_post = cursor.fetchone()
    if deleted_post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id: {id} not found"
        )
    conn.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT) # ______ we deleted the post, we should not send any data back fast api throws an arror if we return the id of the post or something more

@app.put("/posts/{id}", status_code=status.HTTP_200_OK)
def update_post(id: int, post: Post):
    # index = find_index(id)
    # payload_dict = payload.model_dump()
    cursor.execute(
        """UPDATE products SET title=%s, content=%s, published=%s WHERE id=%s RETURNING *""",
        (post.title, post.content, post.published, str(id))
    )
    updated_post = cursor.fetchone()
    if updated_post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"post with id: {id} not found"
        )
    conn.commit()
    return {"data": updated_post} # equals to return JSONResponse(content=jsonable_encoder(payload_dict))
