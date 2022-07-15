from pydantic import BaseSettings

class Settings(BaseSettings):
    OPEN_WEATHER_KEY: str
    DATABASE: str
    REDIS_URL: str
    SECRET: str
    ALGORITHM:str
    BACKEND_URL: str

    class Config:
        env_file = ".env"