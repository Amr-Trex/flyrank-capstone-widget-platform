#!/bin/sh
set -e

echo "Running database migrations..."
python scripts/migrate.py

echo "Seeding demo data..."
python scripts/seed.py

echo "Starting application..."
exec "$@"