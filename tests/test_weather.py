import datetime 

from fastapi.testclient import TestClient

import pytest

from main import app
from settings import Settings

settings = Settings()

client = TestClient(app)


test_data_cities = [ 
    ("london",),
    ("beijing",),
    ("tokyo",),
    ("california",),
]

@pytest.fixture
def list_cities():
    payload = {
    "cities": [
        {"name": "London"},
        {"name": "Tokyo"},
        {"name": "Shanghai"},
        {"name": "Hamburg"},
        {"name": "Mexico"},
    ]
    }
    return payload


@pytest.mark.parametrize("city", test_data_cities)
def test_current_weather(city):
    """
    WHEN GET "/weather/current/{city}" requested
    THEN check that response is valid
    """
    response = client.get(f"/weather/current/{city}")
    assert response.status_code == 200


@pytest.mark.parametrize("city", test_data_cities)
def test_statistic_json_5_days(city):
    """
    WHEN GET "/weather/forecast/{city}" requested
    THEN check that response is valid
    """
    response = client.get(f"/weather/forecast/{city}")
    assert response.status_code == 200


def test_current_chart_city_list(list_cities):
    """
    WHEN GET "weather/current/cities" requested
    THEN check that response is valid
    """
    response = client.get(f"/weather/chart/cities", json=list_cities)
    assert response.status_code == 200


def test_map_cities(list_cities):
    """
    WHEN GET "weather/map/cities" requested
    THEN check that response is valid
    """
    response = client.get(f"/weather/map/cities", json=list_cities)
    assert response.status_code == 200


@pytest.mark.parametrize("city", test_data_cities)
def test_pollution_forecast(city):
    """
    WHEN GET "weather/pollution/forecast/chart/{city}" requested
    THEN check that response is valid
    """
    response = client.get(f"/weather/pollution/forecast/{city}")
    assert response.status_code == 200

