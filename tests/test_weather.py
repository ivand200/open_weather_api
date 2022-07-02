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
    WHEN GET "/weather/statistic/json/{city}" requested
    THEN check that response is valid
    """
    response = client.get(f"/weather/statistic/json/{city}")
    response_body = response.json()
    assert len(response_body) > 5
    assert response.status_code == 200


# @pytest.mark.parametrize("city", test_data_cities)
# def test_statistic_chart_5_days(city):
#     """
#     WHEN GET "/weather/statistic/chart/{city}" requested
#     THEN check that response is valid
#     """
#     response = client.get(f"/weather/statistics/chart/{city}")
#     assert response.status_code == 200
