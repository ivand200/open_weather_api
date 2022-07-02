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
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder

from geopy.geocoders import Nominatim

import requests
import json
import logging
from datetime import date

from schemas.weather import CurrentWeather
from settings import Settings


geolocator = Nominatim(user_agent="weather_app")

router = APIRouter()


settings = Settings()

logger = logging.getLogger()
logger.setLevel(logging.INFO)
handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.INFO)
format = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler.setFormatter(format)
logger.addHandler(handler)


def get_today():
    today_raw = date.today()
    return today_raw.strftime("%d-%m-%Y")


@router.get(
    "/current/{city}", response_model=CurrentWeather, status_code=status.HTTP_200_OK
)
def get_current_temperature(city: str, units: str = "metric"):
    """
    Get current weather by city
    Optional[units]: default = metric
    metric = Celsius
    imperial = Fahrenheit
    """
    location = geolocator.geocode(city)
    logger.info(f"place: {city} | lat: {location.latitude} | lon: {location.longitude}")
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
    )
    return weather
