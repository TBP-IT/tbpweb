PIP_HOME = $(shell python3 -c "import site; import os; print(os.path.join(site.USER_BASE, 'bin'))" \
	|| python -c "import site; import os; print(os.path.join(site.USER_BASE, 'bin'))")

IP ?= 0.0.0.0
PORT ?= 3000

.PHONY: run
run:
	pipenv run python3 ./manage.py runserver $(IP):$(PORT)

.PHONY: superuser
superuser:
	pipenv run python3 ./manage.py createsuperuser

.PHONY: migrations
migrations:
	pipenv run python3 ./manage.py makemigrations

.PHONY: migrate
migrate:
	pipenv run python3 ./manage.py migrate