from pydantic import BaseModel

class PostBase(BaseModel):
    """
    Validator class to ensure data is received in an expected way
    from our `/createposts` endpoint.
    """
    title: str
    content: str
    is_published: bool = True # optional field with default value

class PostCreate(PostBase):
    pass
