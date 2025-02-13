from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_rate_limiting():
    payload = {"text": "rate limit test"}
    # Make 5 successful requests
    for i in range(5):
        response = client.post("/api/v1/moderate/text", json=payload)
        # assuming our fake Celery task is patched in other tests,
        # each successful call should return 200
        assert response.status_code == 200

    # The 6th request should exceed the rate limit
    response = client.post("/api/v1/moderate/text", json=payload)
    assert response.status_code == 429
