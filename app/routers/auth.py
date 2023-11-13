from fastapi import APIRouter, Depends, status,  HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from app import models, oath2, schemas

from app.database import SessionLocal, get_db
from app.utils import verify

router = APIRouter(tags=["Authentication"])

@router.post("/login", response_model=schemas.Token)
def login(user_credentials: OAuth2PasswordRequestForm = Depends(), db: SessionLocal = Depends(get_db)):
    user = db.query(models.User).filter(
        # We use `.username` because OAuth2PasswordRequestForm only has username and password as fields
        # (An email can be used as a username so it is valid)
        models.User.email==user_credentials.username
    ).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Invalid Credentials"
        )
    
    if not verify(user_credentials.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Invalid Credentials"
        )

    access_token = oath2.create_access_token(data={"user_id": user.id})

    return {"access_token": access_token, "token_type": "bearer"}