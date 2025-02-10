#!/bin/bash
set -e

# Wait for database to be ready
python scripts/wait_for_db.py

# Create database if it doesn't exist
python scripts/init_db.py

# Run migrations
alembic upgrade head

# Start the application
uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload 