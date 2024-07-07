install:
	poetry install
dev:
	poetry run flask --app page_analyzer:app run
PORT ?= 8000
start:
	poetry run gunicorn -w 5 -b 0.0.0.0:$(PORT) page_analyzer:app
lint:
	poetry run flake8
l:
	poetry run flake8
test:
	poetry run pytest --cov=page_analyzer
build:
	./build.sh
selfcheck:
	poetry check
test-coverage:
	poetry run pytest --cov=page_analyzer --cov-report xml
check:
	poetry check