gunicorn setup.wsgi:application --bind 0.0.0.0:8000

set -e

python manage.py migrate
python manage.py dump_tutoriais
python manage.py collectstatic --noinput
gunicorn setup.wsgi:application --bind 0.0.0.0:8000