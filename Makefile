PIP_HOME = $(shell python3 -c "import site; import os; print(os.path.join(site.USER_BASE, 'bin'))" \
	|| python -c "import site; import os; print(os.path.join(site.USER_BASE, 'bin'))")

VENV := .venv
BIN := $(VENV)/bin
PYTHON := $(BIN)/python
# MANAGE := $(PYTHON) ./manage.py
MANAGE := TBPWEB_MODE='dev' $(PYTHON) ./manage.py

IP ?= 0.0.0.0
PORT ?= 3000

.PHONY: run
run:
	$(MANAGE) runserver $(IP):$(PORT)

.PHONY: superuser
superuser:
	$(MANAGE) createsuperuser

.PHONY: makemigrations
makemigrations:
	$(MANAGE) makemigrations

.PHONY: migrate
migrate:
	$(MANAGE) migrate

.PHONY: venv
venv:
	python3 -m venv $(VENV)
	@echo "When developing, activate the virtualenv with 'source .venv/bin/activate' so Python can access the installed dependencies."

.PHONY: install-prod
install-prod:
	# For issues with binary packages, consider https://pythonwheels.com/
	$(PYTHON) -m pip install --upgrade "pip<=20.3.4"
	$(PYTHON) -m pip install --upgrade "setuptools<=51.2.0"
	# TODO: pinned/unpinned dependency version.
	# See https://hkn-mu.atlassian.net/browse/COMPSERV-110
	$(PYTHON) -m pip install -r requirements.txt

.PHONY: install
install:
	make install-prod
	$(PYTHON) -m pip install -r requirements-dev.txt

.PHONY: mysql
mysql:
	mysql -e "CREATE DATABASE IF NOT EXISTS tbp;"
	mysql -e "GRANT ALL PRIVILEGES ON tbp.* TO 'tbp'@'localhost' IDENTIFIED BY 'tbpweb-dev';"
