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
from plotly.subplots import make_subplots

import requests
import json
import logging
from datetime import date, datetime, timezone, tzinfo

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



def get_local_time(utc):
    return utc.replace(tzinfo=timezone.utc).astimezone(tz=None)

def get_city(city: str):
    location = geolocator.geocode(city)
    return location

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
    logger.info(
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
    )
    return weather


@router.get("/forecast/json/{city}", status_code=status.HTTP_200_OK)
async def get_stat_json_city(city: str, units: str = "metric"):
    """
    Get weather forecast for next 5 days
    with every 3 hours
    """
    location = geolocator.geocode(city)
    response = requests.post(
        f"https://api.openweathermap.org/data/2.5/forecast?lat={location.latitude}&lon={location.longitude}&units={units}&appid={settings.OPEN_WEATHER_KEY}"
    ).json()
    logger.info(
        f"city forecast: {city} | lat: {location.latitude} | lon: {location.longitude}"
    )
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
    "/forecast/chart/{city}", response_class=FileResponse, status_code=status.HTTP_200_OK
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
    logger.info(
        f"city bar chart forecast: {city} | lat: {location.latitude} | lon: {location.longitude}"
    )
    json_data = jsonable_encoder(response)
    temp = [i["main"]["feels_like"] for i in json_data["list"]]
    time = [i["dt_txt"] for i in json_data["list"]]
    data = {"temperature": temp, "date": time}
    df = pd.DataFrame(data=data)
    df["date"] = pd.to_datetime(df.date)
    # df["time"] = df["time"].dt.strftime("%d/%m/%Y")
    # fig = px.line(df, x="date", y="temperature", markers=True)
    fig = px.scatter(
        df,
        x="date",
        y="temperature",
        title=f"Weather forecast for next 5 days for: {city}",
        trendline="ols",
    )
    fig.write_html(f"stats/{city}.html")
    return FileResponse(f"stats/{city}.html")


@router.get(
    "/chart/cities", response_class=FileResponse, status_code=status.HTTP_200_OK
)
async def get_cities_chart(city_list: CityList, units: str = "metric"):
    """
    Get current weather bar chart for citites list
    """
    cities = tuple(city.name for city in city_list.cities)
    logger.info(f"cities bar chart: {cities}")
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
    df = pd.DataFrame.from_dict(
        data, orient="index", columns=["latitude", "longitude", "temperature"]
    )
    # df.index.name = "city"
    fig = px.bar(
        df,
        x=df.index,
        y="temperature",
        title=f"Current temperature for {[i for i in df.index]}",
        color=df.index,
    )
    # fig.show()
    fig.write_html(f"stats/{[i for i in df.index]}.html")
    return FileResponse(f"stats/{[i for i in df.index]}.html")


@router.get(
    "/map/cities", response_class=FileResponse, status_code=status.HTTP_200_OK
)
async def get_cities_map(city_list: CityList, units: str = "metric"):
    """
    Get map with temperature from the cities list
    """
    cities = tuple(city.name for city in city_list.cities)
    logger.info(f"cities map: {cities}")
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
    df = pd.DataFrame.from_dict(
        data, orient="index", columns=["latitude", "longitude", "temperature"]
    )
    df.index.name = "city"
    fig = px.scatter_geo(
        df,
        lat="latitude",
        lon="longitude",
        color=df.index,
        hover_name=df.index,
        size="temperature",
        projection="natural earth",
    )
    # fig.show()
    fig.write_html(f"stats/map_{[i for i in df.index]}.html")
    return FileResponse(f"stats/map_{[i for i in df.index]}.html")


@router.get(
    "/pollution/forecast/chart/{city}", response_class=FileResponse, status_code=status.HTTP_200_OK
)
async def get_pollution_chart(city: str):
    """
    Get forecast pollution chart for the city
    """
    logger.info(f"chart pollution forecast for {city}")
    loc = get_city(city)
    response = requests.get(
        f"http://api.openweathermap.org/data/2.5/air_pollution/forecast?lat={loc.latitude}&lon={loc.longitude}&appid={settings.OPEN_WEATHER_KEY}"
    ).json()
    data = [
        {
            "date": i["dt"],
            "CO": i["components"]["co"],
            "NO2": i["components"]["no2"],
            "O3": i["components"]["o3"],
            "SO2": i["components"]["so2"],
        }
        for i in response["list"]
    ]
    df = pd.DataFrame.from_dict(data)
    city_name = (loc.raw["display_name"]).split()[0].replace(",", "")
    fig = make_subplots(rows=2, cols=2, subplot_titles=("CO", "NO2", "O3", "SO2"))
    fig.add_trace(go.Scatter(x=df["date"], y=df["CO"]), row=1, col=1)
    fig.add_trace(go.Scatter(x=df["date"], y=df["NO2"]), row=1, col=2)
    fig.add_trace(go.Scatter(x=df["date"], y=df["O3"]), row=2, col=1)
    fig.add_trace(go.Scatter(x=df["date"], y=df["SO2"]), row=2, col=2)
    fig.update_layout(
        height=700, width=1400, title_text=f"Air pollution forecast for {city_name}"
    )
    # fig.show()
    fig.write_html(f"stats/pollution_{city_name}.html")
    return FileResponse(f"stats/pollution_{city_name}.html")
