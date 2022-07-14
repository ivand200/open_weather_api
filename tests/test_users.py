from yaml import Token
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from sqlalchemy import select, text

import pytest

from main import app
from settings import Settings
from db import engine

settings = Settings()

client = TestClient(app)


@pytest.fixture
def get_user():
    payload = {
        "login": "user_test@example.com",
        "password": "Test_pas5"
    }
    return payload


@pytest.fixture
def get_user_with_bad_password():
    payload = {
        "login": "user_test@example.com",
        "password": "Test_pass"
    }
    return payload


@pytest.fixture
def user_signup(get_user):
    response = client.post("users/signup", json=get_user)
    return response


@pytest.fixture
def get_token(get_user):
    response = client.post("users/signup", json=get_user)
    response_body = response.json()
    return response_body["access_token"]


"""Signup TEST"""

def test_signup_wrong_pass(get_user_with_bad_password):
    """
    WHEN "users/signup" requested POST
    with wrong password
    THEN check impossible to signup
    """
    response = client.post(f"users/signup", json=get_user_with_bad_password)
    assert response.status_code == 422


def test_signup(get_user):
    """
    WHEN "users/signup" requested POST
    THEN check response is valid
    """
    response = client.post(f"users/signup", json=get_user)
    response_body = response.json()
    assert len(response_body["access_token"]) > 5
    assert response.status_code == 201


def test_signup_existing_login(get_user):
    """
    WHEN "users/signup" requested POST
    with existing login
    THEN check impossible to signup
    """
    response = client.post(f"users/signup", json=get_user)
    assert response.status_code == 400
    print(get_user['login'])

    with engine.connect().execution_options(autocommit=True) as conn:
        conn.exec_driver_sql("DELETE FROM users WHERE login=(%(val)s)",[{"val": get_user["login"]}])


"""Login test"""

def test_login(get_user, user_signup):
    """
    WHEN "users/login" requested POST
    THEN check response is valid
    """
    user_signup
    response = client.post("users/login", json=get_user)
    assert response.status_code == 200


def test_login_wrong_pass(get_user, get_user_with_bad_password):
    """
    WHEN "users/login" requested POST
    with wrong password
    THEN check impossible to login
    """
    response = client.post("users/login", json=get_user_with_bad_password)
    assert response.status_code == 422

    with engine.connect().execution_options(autocommit=True) as conn:
        conn.exec_driver_sql("DELETE FROM users WHERE login=(%(val)s)",[{"val": get_user["login"]}])


"""Logout TEST"""

def test_logout(get_token, get_user):
    """
    WHEN "users/logout" POST
    THEN check response is valid
    """
    token = get_token
    response = client.post("users/logout", headers={"token": token})
    assert response.status_code == 204

    with engine.connect().execution_options(autocommit=True) as conn:
        conn.exec_driver_sql("DELETE FROM blacklist WHERE token=(%(val)s)",[{"val": token}])
        conn.exec_driver_sql("DELETE FROM users WHERE login=(%(val)s)", [{"val": get_user["login"]}])


def test_blacklist(user_signup):
    """
    WHEN "users/items/new" POST
    after logout
    Theck check impossible to post with token from blacklist
    """
    result = user_signup.json()
    token = result["access_token"]
    response_logout = client.post("users/logout", headers={"token": token})
    assert response_logout.status_code == 204

    response_create_item = client.post("users/items/new", headers={"token": token}, json={"title": "first"})
    response_create_item.status_code == 401

    with engine.connect().execution_options(autocommit=True) as conn:
        conn.exec_driver_sql("DELETE FROM users WHERE login=(%(val)s)", [{"val": "user_test@example.com"}])
        conn.exec_driver_sql("DELETE FROM blacklist WHERE token=(%(val)s)", [{"val": token}])



