format:
	ruff check --exit-zero --fix .
	ruff format .

test:
	pytest -v .

coverage:
	pytest -v --cov --cov-report html .

db:
	docker compose up -d db

run:
	gunicorn setup.wsgi:application --bind 0.0.0.0:8000 --reload

migrations:
	python3 manage.py makemigrations

migrate:
	python3 manage.py migrate

restart_db:
	docker compose down
	docker compose up -d db

data_dev:
	python3 manage.py load_fixtures_dev

data:
	python3 manage.py load_fixtures

dump_tutoriais:
	python3 manage.py dump_tutoriais

fixtures:
	python3 manage.py make_fixtures

restart_db_dev:
	python3 manage.py restart_db_dev

restart_permissoes_escola:
	python3 manage.py reset_permissoes_escola

restart_permissoes_secretaria:
	python3 manage.py reset_permissoes_secretaria

setup-dev:
	pip install -r requirements.txt --no-cache
	pre-commit install