#!/bin/sh
set -e

echo "Step 1: Upload data to PostgreSQL..."
python upload_db.py