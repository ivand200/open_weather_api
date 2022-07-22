import sys

from fastapi import (
    APIRouter,
    Body,
    status,
    Depends,
    HTTPException,
    Header,
    Response,
)

from fastapi.responses import JSONResponse, HTMLResponse, FileResponse
from fastapi.encoders import jsonable_encoder

import requests
import json
import logging
from datetime import date, datetime, timezone, tzinfo
from geopy.geocoders import Nominatim

from schemas.weather import CurrentWeather, CityList
from settings import Settings

settings = Settings()

# geolocator = Nominatim(user_agent="weather_app")
from .weather import get_city, get_today

router = APIRouter()

logger_api = logging.getLogger(__name__)
logger_api.setLevel(logging.INFO)
handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.INFO)
format = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
handler.setFormatter(format)
logger_api.addHandler(handler)


@router.get(
    "/current/{city}", response_model=CurrentWeather, status_code=status.HTTP_200_OK
)
async def get_current_temperature(city: str, units: str = "metric"):
    """
    Get current weather by city
    Optional[units]: default = metric
    metric = Celsius
    imperial = Fahrenheit
    """
    location = get_city(city)
    logger_api.info(
        f"place: {city} | lat: {location.latitude} | lon: {location.longitude}"
    )
    response = requests.post(
        f"https://api.openweathermap.org/data/2.5/weather?lat={location.latitude}&lon={location.longitude}&units={units}&appid={settings.OPEN_WEATHER_KEY}"
    ).json()
    data = jsonable_encoder(response)
    weather = CurrentWeather(
        place=data["name"],
        today=get_today(),
        temperature=data["main"]["feels_like"],
        description=data["weather"][0]["description"],
        wind=data["wind"]["speed"],
        pressure=data["main"]["pressure"],
        humidity=data["main"]["humidity"],
    )
    return weather


@router.get("/forecast/{city}", status_code=status.HTTP_200_OK)
async def get_stat_json_city(city: str, units: str = "metric"):
    """
    Get weather forecast for next 5 days
    with every 3 hours
    """
    location = get_city(city)
    response = requests.post(
        f"https://api.openweathermap.org/data/2.5/forecast?lat={location.latitude}&lon={location.longitude}&units={units}&appid={settings.OPEN_WEATHER_KEY}"
    ).json()
    logger_api.info(
        f"city forecast: {city} | lat: {location.latitude} | lon: {location.longitude}"
    )
    json_data = jsonable_encoder(response)
    result = [
        {"date": i["dt_txt"], "temperature": i["main"]["feels_like"]}
        for i in json_data["list"]
    ]
    return JSONResponse(result)
