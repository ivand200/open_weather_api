from fastapi import FastAPI

from routers.weather import router as router_weather
from routers.users import router as router_users

app = FastAPI()

app.include_router(
    router_weather,
    prefix="/weather",
    tags=["weather"]
)

app.include_router(
    router_users,
    prefix="/users",
    tags=["users"]
)
