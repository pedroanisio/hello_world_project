# Build stage
FROM python:3.11-slim-bookworm as builder

WORKDIR /build

# Install build dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Runtime stage
FROM python:3.11-slim-bookworm

WORKDIR /app

# Install OS dependencies
RUN apt-get update && \
    apt-get install -y netcat-traditional postgresql-client && \
    rm -rf /var/lib/apt/lists/*

# Copy Python packages from builder
COPY --from=builder /usr/local/lib/python3.11/site-packages/ /usr/local/lib/python3.11/site-packages/
COPY --from=builder /usr/local/bin/ /usr/local/bin/

# Set environment variables
ENV PYTHONPATH=/app
ENV ENVIRONMENT=dev

# Copy the project files into the container
COPY . .
