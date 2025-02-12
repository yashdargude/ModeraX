# filepath: /Users/yashdargude/Downloads/steps_AI/Dockerfile

FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY . .

# CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

CMD uvicorn main:app