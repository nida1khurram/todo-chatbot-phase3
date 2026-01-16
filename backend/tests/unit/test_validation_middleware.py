import pytest
from fastapi.testclient import TestClient
from fastapi import FastAPI
from starlette.middleware import Middleware
from src.middleware.validation import ValidationMiddleware


def test_validation_middleware_valid_data():
    """Test that valid data passes through the middleware"""
    # Create a simple app with validation middleware
    app = FastAPI()
    app.add_middleware(ValidationMiddleware)

    @app.post("/test")
    async def test_endpoint(data: dict):
        return data

    client = TestClient(app)

    # Send valid data
    response = client.post("/test", json={
        "email": "test@example.com",
        "password": "validpassword123"
    })

    assert response.status_code == 200


def test_validation_middleware_invalid_email():
    """Test that invalid email is rejected"""
    # Create a simple app with validation middleware
    app = FastAPI()
    app.add_middleware(ValidationMiddleware)

    @app.post("/test")
    async def test_endpoint(data: dict):
        return data

    client = TestClient(app)

    # Send invalid email
    response = client.post("/test", json={
        "email": "invalid-email",
        "password": "validpassword123"
    })

    assert response.status_code == 400
    data = response.json()
    assert "detail" in data


def test_validation_middleware_weak_password():
    """Test that weak password is rejected"""
    # Create a simple app with validation middleware
    app = FastAPI()
    app.add_middleware(ValidationMiddleware)

    @app.post("/test")
    async def test_endpoint(data: dict):
        return data

    client = TestClient(app)

    # Send weak password
    response = client.post("/test", json={
        "email": "test@example.com",
        "password": "123"  # Too short
    })

    assert response.status_code == 400
    data = response.json()
    assert "detail" in data


def test_validation_middleware_valid_password():
    """Test that valid password passes validation"""
    # Create a simple app with validation middleware
    app = FastAPI()
    app.add_middleware(ValidationMiddleware)

    @app.post("/test")
    async def test_endpoint(data: dict):
        return data

    client = TestClient(app)

    # Send valid password
    response = client.post("/test", json={
        "email": "test@example.com",
        "password": "validpassword123"
    })

    assert response.status_code == 200


def test_validation_middleware_empty_email():
    """Test that empty email is rejected"""
    # Create a simple app with validation middleware
    app = FastAPI()
    app.add_middleware(ValidationMiddleware)

    @app.post("/test")
    async def test_endpoint(data: dict):
        return data

    client = TestClient(app)

    # Send empty email
    response = client.post("/test", json={
        "email": "",
        "password": "validpassword123"
    })

    assert response.status_code == 400
    data = response.json()
    assert "detail" in data


def test_validation_middleware_missing_email():
    """Test that missing email field passes if not required by endpoint"""
    # Create a simple app with validation middleware
    app = FastAPI()
    app.add_middleware(ValidationMiddleware)

    @app.post("/test")
    async def test_endpoint(data: dict):
        return data

    client = TestClient(app)

    # Send data without email field
    response = client.post("/test", json={
        "some_other_field": "value"
    })

    assert response.status_code == 200