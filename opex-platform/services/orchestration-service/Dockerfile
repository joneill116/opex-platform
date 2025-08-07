FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y gcc g++ && rm -rf /var/lib/apt/lists/*

# Copy and install shared package
COPY packages/python-common /packages/python-common
RUN pip install -e /packages/python-common

# Install service dependencies
COPY services/orchestration-service/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy service code
COPY services/orchestration-service .

# Set Python path to include src directory
ENV PYTHONPATH=/app/src:$PYTHONPATH

# Run migrations and start service
CMD ["sh", "-c", "alembic upgrade head && uvicorn src.main:app --host 0.0.0.0 --port 8000"]
