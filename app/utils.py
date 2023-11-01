from passlib.context import CryptContext

# we are telling passlib what is the default hasing algorithm (-> bcrypt)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str):
    return pwd_context.hash(password)