#!/bin/sh
# entrypoint.sh

set -e

# Fix database schema first
echo "Fixing database schema..."
python manage.py fix_database_schema || echo "Schema fix failed, but continuing..."

# Run Django migrations
echo "Running Django migrations..."
python manage.py migrate --noinput

# Create superuser (non-blocking)
echo "Attempting to create or update superuser..."
python manage.py createsu || echo "Superuser creation failed, but continuing..."

# Collect static files for production
echo "Collecting static files..."
python manage.py collectstatic --noinput || echo "Static files collection failed, but continuing..."

echo "Django migrations complete."

# Start the Daphne server
echo "Starting Daphne server..."
exec python -m daphne bingo_project.asgi:application -b 0.0.0.0 -p $PORT
