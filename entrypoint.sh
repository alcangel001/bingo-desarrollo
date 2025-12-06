#!/bin/sh
# entrypoint.sh

# No usar set -e para permitir manejo de errores
set +e

# Run Django migrations
echo "Running Django migrations..."
python manage.py migrate --noinput
MIGRATE_EXIT=$?

if [ $MIGRATE_EXIT -ne 0 ]; then
    echo "Migration failed with exit code $MIGRATE_EXIT"
    echo "This might be due to a corrupted transaction state."
    echo "Trying to continue anyway..."
fi

# Create superuser (non-blocking)
echo "Attempting to create or update superuser..."
python manage.py createsu || echo "Superuser creation failed, but continuing..."

# Collect static files for production
echo "Collecting static files..."
python manage.py collectstatic --noinput || echo "Static files collection failed, but continuing..."

echo "Django setup complete."

# Start the Daphne server
echo "Starting Daphne server..."
exec python -m daphne bingo_project.asgi:application -b 0.0.0.0 -p $PORT
