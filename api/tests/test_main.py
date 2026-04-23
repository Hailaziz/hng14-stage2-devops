import pytest
from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Mock redis before importing app
mock_redis = MagicMock()
with patch('redis.Redis', return_value=mock_redis):
    from main import app

client = TestClient(app)

def setup_function():
    mock_redis.reset_mock()

def test_health_endpoint():
    mock_redis.ping.return_value = True
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_create_job():
    mock_redis.lpush.return_value = 1
    mock_redis.hset.return_value = 1
    response = client.post("/jobs")
    assert response.status_code == 200
    data = response.json()
    assert "job_id" in data
    assert len(data["job_id"]) == 36  # UUID format

def test_get_job_found():
    mock_redis.hget.return_value = "completed"
    response = client.get("/jobs/test-job-123")
    assert response.status_code == 200
    data = response.json()
    assert data["job_id"] == "test-job-123"
    assert data["status"] == "completed"

def test_get_job_not_found():
    mock_redis.hget.return_value = None
    response = client.get("/jobs/nonexistent-job")
    assert response.status_code == 200
    assert "error" in response.json()

def test_create_job_pushes_to_queue():
    mock_redis.lpush.return_value = 1
    mock_redis.hset.return_value = 1
    response = client.post("/jobs")
    assert response.status_code == 200
    mock_redis.lpush.assert_called_once()
    mock_redis.hset.assert_called_once()
