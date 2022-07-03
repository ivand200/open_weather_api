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

from geopy.geocoders import Nominatim
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

import requests
import json
import logging
from datetime import date, datetime

from schemas.weather import CurrentWeather, CityList
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
async def get_current_temperature(city: str, units: str = "metric"):
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


@router.get("/statistic/json/{city}", status_code=status.HTTP_200_OK)
async def get_stat_json_city(city: str, units: str = "metric"):
    """
    Get weather forecast for next 5 days
    with every 3 hours
    """
    location = geolocator.geocode(city)
    response = requests.post(
        f"https://api.openweathermap.org/data/2.5/forecast?lat={location.latitude}&lon={location.longitude}&units={units}&appid={settings.OPEN_WEATHER_KEY}"
    ).json()
    logger.info(f"city: {city} | lat: {location.latitude} | lon: {location.longitude}")
    json_data = jsonable_encoder(response)
    result = [
        {
            "date": i["dt_txt"],
            "temperature": i["main"]["feels_like"]
        }
        for i in json_data["list"]
    ]
    return JSONResponse(result)


@router.get(
    "/statistic/chart/{city}", response_class=FileResponse, status_code=status.HTTP_200_OK
)
async def get_stat_chart_by_city(city: str, units: str = "metric"):
    """
    Get weather forecast for next 5 days
    Return html chart
    Optional[units]: default = metric
    metric = Celsius
    imperial = Fahrenheit
    """
    location = geolocator.geocode(city)
    response = requests.post(
        f"https://api.openweathermap.org/data/2.5/forecast?lat={location.latitude}&lon={location.longitude}&units={units}&appid={settings.OPEN_WEATHER_KEY}"
    ).json()
    logger.info(f"city: {city} | lat: {location.latitude} | lon: {location.longitude}")
    json_data = jsonable_encoder(response)
    temp = [i["main"]["feels_like"] for i in json_data["list"]]
    time = [i["dt_txt"] for i in json_data["list"]]
    data = {"temperature": temp, "date": time}
    df = pd.DataFrame(data=data)
    df["date"] = pd.to_datetime(df.date)
    # df["time"] = df["time"].dt.strftime("%d/%m/%Y")
    # fig = px.line(df, x="date", y="temperature", markers=True)
    fig = px.scatter(df, x="date", y="temperature", trendline="ols")
    fig.write_html(f"stats/{city}.html")
    return FileResponse(f"stats/{city}.html")


@router.get("/map", status_code=status.HTTP_200_OK)
async def get_weather_map(city_list: CityList, units: str = "metric"):
    """
    Get weather bar chart for citites list
    """
    cities = tuple(city.name for city in city_list.cities)
    data = {}
    for city in cities:
        location = geolocator.geocode(city)
        response = requests.post(
            f"https://api.openweathermap.org/data/2.5/weather?lat={location.latitude}&lon={location.longitude}&units={units}&appid={settings.OPEN_WEATHER_KEY}"
        ).json()
        data[city] = (
            location.latitude,
            location.longitude,
            response["main"]["feels_like"],
        )
    #df = pd.DataFrame.from_dict(data)
    df = pd.DataFrame.from_dict(
        data, orient="index", columns=["latitude", "longitude", "temperature"]
    )
    df.index.name = "city"
    fig = px.bar(
        df,
        x=df.index,
        y="temperature",
        title=f"Current temperature for {[i for i in df.index]}",
        color=df.index,
    )
    return fig.show()
