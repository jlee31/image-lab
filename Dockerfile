FROM python:3.12-slim

WORKDIR /app

# Install system deps for OpenCV
RUN apt-get update && \
    apt-get install -y --no-install-recommends libgl1 libglib2.0-0 && \
    rm -rf /var/lib/apt/lists/*

# Install Python deps
COPY requirements-api.txt ./
RUN pip install --no-cache-dir -r requirements-api.txt

# Copy application code
COPY api/ api/
COPY processing/ processing/
COPY utils/ utils/
COPY web/ web/

EXPOSE 8000

CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
