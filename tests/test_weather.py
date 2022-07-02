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

    """
    response = client.get(f"/weather/current/{city}")
    assert response.status_code == 200