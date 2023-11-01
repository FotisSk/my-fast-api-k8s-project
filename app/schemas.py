from pydantic import BaseModel, EmailStr
from datetime import datetime

class PostBase(BaseModel):
    """
    Validator class to ensure data is received in an expected way
    from our endpoint.
    """
    title: str
    content: str
    published: bool = True # optional field with default value


class PostCreate(PostBase):
    """
    Validator class to ensure data is received in an expected way
    from our endpoint in order to create a Post.
    """
    pass


class PostResponse(PostBase):
    """
    Response related class to ensure which Post data is returned/ommited.
    """
    id: int
    created_at: datetime

    #Tells pydantic model to read the data even if it is not a dict, but an ORM model
    #(or any other arbitrary obj with attributes).
    class Config:
        orm_mode = True


class UserCreate(BaseModel):
    """
    Validator class to ensure data is received in an expected way
    from our endpoint in order to create a User.
    """
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    """
    Response related class to ensure which User data is returned/ommited.
    """
    id: int
    email: EmailStr
    created_at: datetime

    class Config:
        orm_mode = True
