FROM python:3.11-slim-bookworm

WORKDIR /app

# Install OS dependencies
RUN apt-get update && \
    apt-get install -y netcat-traditional postgresql-client && \
    rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Set environment variables
ENV PYTHONPATH=/app
ENV ENVIRONMENT=dev

# Copy the project files into the container
COPY . .
