from lib2to3.pytree import Base
from pydantic import BaseSettings

class Settings(BaseSettings):
    OPEN_WEATHER_KEY: str

    class Config:
        env_file = ".env"