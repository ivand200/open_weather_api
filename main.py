from fastapi import FastAPI

from routers.weather import router as router_weather
from routers.users import router as router_users
from routers.api import router as router_api

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

app.include_router(
    router_api,
    prefix="/api/v1",
    tags=["api"]
)