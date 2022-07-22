import datetime 

from fastapi.testclient import TestClient

import pytest

from main import app
from settings import Settings
from .test_weather import test_data_cities

settings = Settings()

client = TestClient(app)


@pytest.mark.parametrize("city", test_data_cities)
def test_current_weather(city):
    """
    WHEN GET "/api/v1/current/{city}" requested
    THEN check that response is valid
    """
    response = client.get(f"/api/v1/current/{city}")
    assert response.status_code == 200


@pytest.mark.parametrize("city", test_data_cities)
def test_statistic_json_5_days(city):
    """
    WHEN GET "/api/v1/forecast/{city}" requested
    THEN check that response is valid
    """
    response = client.get(f"/api/v1/forecast/{city}")
    response_body = response.json()
    assert len(response_body) > 5
    assert response.status_code == 200