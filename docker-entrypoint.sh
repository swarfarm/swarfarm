#!/bin/sh

if [ "$DATABASE" = "postgres" ]
then
    echo "Waiting for postgres..."

    /app/deployment_assets/wait-for ${SQL_HOST}:${SQL_PORT}

    echo "PostgreSQL started"
fi

# Load initial data and migrations
echo "Collecting Static Files..."
python manage.py collectstatic --no-input

echo "Running database migrations..."
python manage.py migrate

exec "$@"
