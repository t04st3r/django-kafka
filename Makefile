dump-requirements:
	jq -r '.default | to_entries[] | .key + .value.version' Pipfile.lock > requirements.txt
	jq -r '.develop | to_entries[] | .key + .value.version' Pipfile.lock > requirements-dev.txt

migrate:
	python manage.py migrate --noinput

collectstatic:
	python manage.py collectstatic --noinput

populate-models:
	python manage.py populate_models

consume-records:
	python -u manage.py consume_records	

install:
	pip install -r requirements.txt

install-dev:
	pip install -r requirements-dev.txt --pre

test:
	pytest

run-dev:
	python manage.py runserver	