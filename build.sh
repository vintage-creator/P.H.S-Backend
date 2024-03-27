#!/bin/bash

# Stop execution if any command fails
set -o errexit

# Install dependencies
pip install -r requirements.txt

# Apply migrations
python handyman_project/manage.py migrate
