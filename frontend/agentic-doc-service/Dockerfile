FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN useradd -m worker
USER worker
COPY service.py .

CMD ["uvicorn", "service:app", "--host", "0.0.0.0", "--port", "8000"]
