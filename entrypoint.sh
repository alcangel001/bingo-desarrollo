#!/bin/sh
# entrypoint.sh

set -e

# Fix database schema first
echo "Fixing database schema..."
/opt/venv/bin/python manage.py fix_database_schema || echo "Schema fix failed, but continuing..."

# Run Django migrations using absolute path to venv python
echo "Running Django migrations..."
/opt/venv/bin/python manage.py migrate --noinput

# Create superuser (non-blocking)
echo "Attempting to create or update superuser..."
/opt/venv/bin/python manage.py createsu || echo "Superuser creation failed, but continuing..."

# Collect static files for production
echo "Collecting static files..."
/opt/venv/bin/python manage.py collectstatic --noinput || echo "Static files collection failed, but continuing..."

echo "Django migrations complete."

# Start the Daphne server using absolute path to venv python
echo "Starting Daphne server..."
exec /opt/venv/bin/python -m daphne bingo_project.asgi:application -b 0.0.0.0 -p $PORT
