from fastapi import FastAPI, HTTPException, Request, Depends
from pydantic import BaseModel
import requests
import json
from config import OPENAI_API_KEY, OPENAI_API_URL
from openai import OpenAI
from database import engine
from models import Base
from sqlalchemy.orm import Session
from sqlalchemy import text
from database import SessionLocal
from models import ModerationResult

app = FastAPI()
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


# @app.post("/api/v1/moderate/text")
# def moderate_text(request: Request, body: TextModerationRequest):
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "input": body.text
    }
    try:
        response = requests.post(OPENAI_API_URL, headers=headers, json=data)
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code,
                                detail="Error with OpenAI API")
        return response.json()
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/moderate/text")
def moderate_text(request: Request, body: TextModerationRequest, db: Session = Depends(get_db)):
    # Temporary hardcoded response
    hardcoded_response = {
        "id": "modr-1234567890",
        "model": "omni-moderation-latest",
        "results": [
            {
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
                "category_scores": {
                    "hate": 0.01,
                    "hate/threatening": 0.01,
                    "self-harm": 0.01,
                    "sexual": 0.01,
                    "sexual/minors": 0.01,
                    "violence": 0.01,
                    "violence/graphic": 0.01
                }
            }
        ]
    }
    try:
        # Store the result in the database
        moderation_result = ModerationResult(
            model=hardcoded_response["model"],
            results=hardcoded_response["results"]
        )
        db.add(moderation_result)
        db.commit()
        db.refresh(moderation_result)

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error storing data: {str(e)}")

        # Optionally, retrieve the stored record to debug
    stored_record = db.query(ModerationResult).filter(
        ModerationResult.id == moderation_result.id
    ).first()
    print("Stored record:", stored_record)

    return hardcoded_response


@app.get("/api/v1/db-test")
def db_test(db: Session = Depends(get_db)):
    """
    Tests database connectivity by executing a simple query.
    """
    try:
        # Execute a simple test query
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
    # Placeholder for image moderation logic
    raise HTTPException(status_code=501, detail="Not Implemented")


@app.get("/api/v1/moderation/{id}")
def get_moderation_result(id: int):
    # Placeholder for fetching moderation result
    raise HTTPException(status_code=501, detail="Not Implemented")


@app.get("/api/v1/stats")
def get_stats():
    # Placeholder for fetching stats
    raise HTTPException(status_code=501, detail="Not Implemented")
