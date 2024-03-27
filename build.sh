#!/bin/bash

# Stop execution if any command fails
set -o errexit

# Navigate into the directory where manage.py is located
cd handyman_project

# Install dependencies
pip install -r ../requirements.txt

# Apply migrations
python manage.py migrate
