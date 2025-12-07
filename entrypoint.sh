#!/bin/sh
# entrypoint.sh

# No usar set -e para permitir manejo de errores
set +e

# Run Django migrations - intentar varias veces si falla
echo "Running Django migrations..."
python manage.py migrate --noinput
MIGRATE_EXIT=$?

if [ $MIGRATE_EXIT -ne 0 ]; then
    echo "First migration attempt failed, trying again..."
    sleep 2
    python manage.py migrate --noinput
    MIGRATE_EXIT=$?
fi

if [ $MIGRATE_EXIT -ne 0 ]; then
    echo "Migration failed with exit code $MIGRATE_EXIT"
    echo "Checking migration status..."
    python manage.py showmigrations
    echo "Trying to continue anyway, but errors may occur..."
fi

# Setup PercentageSettings (required for system to work)
echo "Setting up PercentageSettings..."
python manage.py setup_percentage_settings || echo "PercentageSettings setup failed, but continuing..."

# Setup Package Templates (required for franchise system)
echo "Setting up Package Templates..."
python manage.py setup_package_templates || echo "Package Templates setup failed, but continuing..."

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
