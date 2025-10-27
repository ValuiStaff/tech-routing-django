web: python manage.py migrate --noinput && gunicorn tech_routing.wsgi:application --bind 0.0.0.0:$PORT --workers 3 --threads 2 --timeout 120 --access-logfile - --error-logfile -
