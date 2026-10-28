FROM python:3.14-slim

WORKDIR /app

# Install packages first, so Docker can reuse this layer when only code changes
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ app/
COPY data/ data/

EXPOSE 8000

# 0.0.0.0 = listen to requests from outside the container, not just inside it
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
