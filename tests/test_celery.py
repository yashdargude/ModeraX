import pytest
from celery_worker import moderate_text_task

# Create a fake response object to simulate requests.post


class FakeResponse:
    def __init__(self, status_code, json_data):
        self.status_code = status_code
        self._json = json_data

    def json(self):
        return self._json


def fake_post(url, headers, json):
    # Return a fake successful JSON response
    return FakeResponse(200, {
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
    })


@pytest.fixture(autouse=True)
def patch_requests(monkeypatch):
    # Patch the requests.post function used in the celery task
    monkeypatch.setattr("celery_worker.requests.post", fake_post)


def test_moderate_text_task():
    result = moderate_text_task("test text")
    assert isinstance(result, dict)
    assert result.get("model") == "omni-moderation-latest"
    assert "results" in result
