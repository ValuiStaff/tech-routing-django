#!/bin/bash

# Activate virtual environment and start Django server
source venv/bin/activate
echo "Virtual environment activated!"
echo "Starting Django development server..."
python manage.py runserver

