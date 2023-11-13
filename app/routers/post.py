from typing import List
from fastapi import Depends, status, HTTPException, APIRouter
from app import models, oath2, schemas
from app.database import get_db
from sqlalchemy.orm import Session

router = APIRouter(
    prefix="/posts",
    tags=["Posts"]
)

# GET ALL POSTS
@router.get("", response_model=List[schemas.PostResponse])
async def get_posts(
    db: Session = Depends(get_db),
    current_user: int = Depends(oath2.get_current_user)
):
    posts = db.query(models.Post).all()
    return posts  
    # FASTAPI automatically serializes posts into JSON
    # return JSONResponse(content=jsonable_encoder(posts))

# GET A POST
@router.get("/{id}", response_model=schemas.PostResponse)
async def get_post(
    id: int, 
    db: Session = Depends(get_db),
    current_user: int = Depends(oath2.get_current_user)
): #___________ id: int means that `id` has to be an integer and it is going to try to convert the `id` to an int every time
    post = db.query(models.Post).filter(models.Post.id==id).first()
    if not post:
        # response.status_code = status.HTTP_404_NOT_FOUND
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"post with id: {id} not found"
        )
    return post

# CREATE A POST
@router.post("", status_code=status.HTTP_201_CREATED, response_model=schemas.PostResponse) # ________ with status_code we are changing the default response
# async def create_posts(payload: dict = Body(...)):
async def create_posts(
    post: schemas.PostCreate,
    db: Session = Depends(get_db),
    current_user: int = Depends(oath2.get_current_user)
):
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
@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(
    id: int,
    db: Session = Depends(get_db),
    current_user: int = Depends(oath2.get_current_user)
):
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
@router.put("/{id}", status_code=status.HTTP_200_OK, response_model=schemas.PostResponse)
def update_post(
    id: int,
    post: schemas.PostCreate, 
    db: Session = Depends(get_db),
    current_user: int = Depends(oath2.get_current_user)
):
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