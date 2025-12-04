#!/bin/bash
set -e

echo "Waiting for PostgreSQL to be ready..."
until python -c "import psycopg2; import os; psycopg2.connect(os.environ['DATABASE_URL'])" 2>/dev/null; do
  echo "PostgreSQL is unavailable - sleeping"
  sleep 2
done

echo "PostgreSQL is ready!"

# Initialize Flask-Migrate if not already done
if [ ! -d "migrations" ]; then
    echo "Initializing database migrations..."
    flask db init
    echo "Creating initial migration..."
    flask db migrate -m "Initial migration - users and generated_images tables"
fi

# Run database migrations
echo "Running database migrations..."
flask db upgrade

# Start the Flask application
echo "Starting Flask application..."
exec python app.py
