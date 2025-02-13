from fastapi import FastAPI, HTTPException, Request, Depends
from pydantic import BaseModel
import json
import requests
import redis
from config import OPENAI_API_KEY, OPENAI_API_URL
from openai import OpenAI
from database import engine
from models import Base, ModerationResult
from sqlalchemy.orm import Session
from sqlalchemy import text
from database import SessionLocal

# Rate limiting imports
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from fastapi.responses import JSONResponse

# Prometheus instrumentation
from prometheus_fastapi_instrumentator import Instrumentator

# Celery task
from celery_worker import moderate_text_task

app = FastAPI()

# Initialize Redis client for caching
redis_client = redis.Redis(host="redis", port=6379,
                           db=0, decode_responses=True)

# Setup rate limiter
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(429, _rate_limit_exceeded_handler)

# Instrument app for Prometheus metrics
Instrumentator().instrument(app).expose(app)

Base.metadata.create_all(bind=engine)


class TextModerationRequest(BaseModel):
    text: str


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


client = OpenAI(api_key=OPENAI_API_KEY)


@app.get("/")
def healthy_get():
    print(f"the keys are {OPENAI_API_KEY}")
    try:
        response = client.moderations.create(
            model="omni-moderation-latest",
            input="harsh mental idiot and weak also the harsher",
        )
        return {"status": f"healthy on the line {response}"}
    except Exception as e:
        raise HTTPException(status_code=429, detail="Rate limit exceeded")


@app.post("/")
def healthy_post():
    return {"status": "healthy"}


# Updated text moderation endpoint with rate limiting and caching
@app.post("/api/v1/moderate/text")
@limiter.limit("5/minute")
def moderate_text(request: Request, body: TextModerationRequest, db: Session = Depends(get_db)):
    cache_key = f"moderation:{body.text}"
    cached = redis_client.get(cache_key)
    if cached:
        return json.loads(cached)

    try:
        # Call Celery task asynchronously
        task = moderate_text_task.delay(body.text)
        # Wait for result with a timeout (or return task.id for async polling)
        result = task.get(timeout=10)
    except Exception as e:
        # Fallback if Celery fails or timeout
        result = {
            "id": "fallback",
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
                "category_scores": {k: 0.01 for k in [
                    "hate", "hate/threatening", "self-harm", "sexual",
                    "sexual/minors", "violence", "violence/graphic"
                ]}
            }]
        }

    # Store the result in the database
    try:
        moderation_result = ModerationResult(
            model=result["model"],
            results=result["results"]
        )
        db.add(moderation_result)
        db.commit()
        db.refresh(moderation_result)
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error storing data: {str(e)}")

    # Cache the response (set expiry as needed, e.g., 10 minutes)
    redis_client.setex(cache_key, 600, json.dumps(result))
    return result


@app.get("/api/v1/db-test")
def db_test(db: Session = Depends(get_db)):
    try:
        result = db.execute(text("SELECT 1")).scalar()
        return {"connection": "successful", "result": result}
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"DB connection failed: {str(e)}")


@app.get("/api/v1/records")
def list_moderation_results(db: Session = Depends(get_db)):
    results = db.query(ModerationResult).all()
    return results


@app.post("/api/v1/moderate/image")
def moderate_image():
    raise HTTPException(status_code=501, detail="Not Implemented")


@app.get("/api/v1/moderation/{id}")
def get_moderation_result(id: int):
    raise HTTPException(status_code=501, detail="Not Implemented")


@app.get("/api/v1/stats")
def get_stats():
    # This endpoint is overridden by Prometheus instrumentation (/metrics)
    raise HTTPException(status_code=501, detail="Not Implemented")
