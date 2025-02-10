#!/bin/bash
set -e

echo "Starting initialization script..."

# Wait for postgres
echo "Waiting for PostgreSQL..."
until nc -z -v -w30 db 5432
do
  echo "Waiting for database connection..."
  sleep 5
done

# Wait for redis
echo "Waiting for Redis..."
until nc -z -v -w30 redis 6379
do
  echo "Waiting for redis connection..."
  sleep 5
done

# Create database if it doesn't exist
echo "Creating database if it doesn't exist..."
# python scripts/init_db.py

echo "Creating initial migration if not exists..."
if [ ! -f "migrations/versions/"* ]; then  
    # Create and apply initial migration
    alembic revision --autogenerate -m "initial"
    alembic upgrade head
else
    # Just run pending migrations
    alembic upgrade head
fi

echo "Seeding database..."
python scripts/seed_db.py

echo "Starting application..."
uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload 