import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_root_returns_200():
    # Just test if the root path exists (returns 200)
    response = client.get("/")
    assert response.status_code == 200

def test_swap_endpoint_exists():
    # Just test if the endpoint exists (returns 422 because no file provided)
    response = client.post("/api/process/swap")
    assert response.status_code == 422

def test_scale_endpoint_exists():
    # Just test if the endpoint exists (returns 422 because no file provided)
    response = client.post("/api/process/scale")
    assert response.status_code == 422
