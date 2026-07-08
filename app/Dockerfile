FROM python:3.11-slim

WORKDIR /app

COPY requirements/base.txt .
COPY requirements/dev.txt .

RUN pip install --no-cache-dir -r base.txt -r dev.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
