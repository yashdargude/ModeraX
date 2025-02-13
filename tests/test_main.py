import json
import pytest
from fastapi.testclient import TestClient
from main import app, redis_client
from models import ModerationResult
from database import SessionLocal

client = TestClient(app)


@pytest.fixture(scope="module", autouse=True)
def cleanup_db():
    # Setup: remove existing ModerationResults before tests
    db = SessionLocal()
    db.query(ModerationResult).delete()
    db.commit()
    yield
    db.query(ModerationResult).delete()
    db.commit()
    db.close()


def test_healthy_get():
    response = client.get("/")
    assert response.status_code == 200
    json_response = response.json()
    assert "status" in json_response


def test_healthy_post():
    response = client.post("/")
    assert response.status_code == 200
    json_response = response.json()
    assert json_response.get("status") == "healthy"


def test_moderate_text_caching(monkeypatch):
    test_text = "this is a caching test"
    cache_key = f"moderation:{test_text}"
    redis_client.delete(cache_key)

    # Patch the Celery task delay method so it returns a fake task
    class FakeTask:
        def get(self, timeout):
            return {
                "id": "fake",
                "model": "omni-moderation-latest",
                "results": [{
                    "flagged": False,
                    "categories": {
                        "hate": False,
                        "hate/threatening": False,
                        "self-harm": False,
                        "sexual": False,
                        "sexual/minors": False,
                        "violence": False,
                        "violence/graphic": False
                    },
                    "category_scores": {k: 0.1 for k in [
                        "hate", "hate/threatening", "self-harm",
                        "sexual", "sexual/minors", "violence", "violence/graphic"
                    ]}
                }]
            }
    monkeypatch.setattr(
        "celery_worker.moderate_text_task.delay", lambda text: FakeTask())

    # First call should not use cache.
    response = client.post("/api/v1/moderate/text", json={"text": test_text})
    assert response.status_code == 200
    data = response.json()
    assert data.get("model") == "omni-moderation-latest"

    # Second call should get result from Redis cache.
    response2 = client.post("/api/v1/moderate/text", json={"text": test_text})
    assert response2.status_code == 200
    data2 = response2.json()
    assert data == data2


def test_db_test():
    response = client.get("/api/v1/db-test")
    assert response.status_code == 200
    data = response.json()
    assert data.get("connection") == "successful"
