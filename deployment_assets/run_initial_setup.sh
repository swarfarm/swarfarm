#!/bin/sh

# Load initial data and migrations
echo "Collecting Static Files..."
python manage.py collectstatic --no-input

echo "Running database migrations..."
python manage.py migrate

echo "Loading initial data..."
python manage.py loaddata bestiary_data
python manage.py loaddata initial_auth_groups
python manage.py loaddata reports
