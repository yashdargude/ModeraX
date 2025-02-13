from celery import Celery

celery_app = Celery(
    "tasks",
    broker="redis://redis:6379/0",
    backend="redis://redis:6379/0"
)


@celery_app.task(bind=True, max_retries=3)
def moderate_text_task(self, text: str):
    import requests
    from config import OPENAI_API_KEY, OPENAI_API_URL
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {"input": text}
    try:
        response = requests.post(OPENAI_API_URL, headers=headers, json=data)
        if response.status_code != 200:
            raise Exception("Error with OpenAI API")
        return response.json()
    except Exception as exc:
        # Exponential backoff: 2**retries seconds delay
        raise self.retry(exc=exc, countdown=2**(self.request.retries))
