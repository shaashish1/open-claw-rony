FROM python:3.12-slim

WORKDIR /app

# Install dependencies
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend and frontend
COPY backend/ /app/backend/
COPY frontend/ /app/frontend/

# Data directory for SQLite
RUN mkdir -p /app/data

WORKDIR /app/backend

EXPOSE 8000

# RULE: DRAFT ONLY - Never call SMTP send
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--log-level", "info"]
