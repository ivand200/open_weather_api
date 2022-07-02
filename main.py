from fastapi import FastAPI
from routers.weather import router as router_weather

app = FastAPI()

app.include_router(
    router_weather,
    prefix="/weather",
    tags=["weather"]
)

