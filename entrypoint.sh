#!/bin/sh

# Exit immediately if a command exits with a non-zero status
set -e

echo "Running data migration and seed script..."
python import_all_csv_data.py

echo "Starting Flask Application..."
exec python app.py