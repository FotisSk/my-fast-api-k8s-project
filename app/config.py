"""
In development environment it is ok to set our environment variables in .env file.
In production environment it is better to set them on the machine.
"""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Performs environment variable validation. All variables must take a value one 
    way or another. Case Insensitive.
    """
    host: str
    database: str
    db_user: str
    password: str
    secret_key: str
    algorithm: str
    access_token_expire_minutes: int

    # tell Pydantic to import them from .env file
    class Config:
        env_file = ".env"


#_Pydantic will read all the environment variables that we declared in `class Settings()`
# and store them in variable `settings` so that we can access them.
settings = Settings()

