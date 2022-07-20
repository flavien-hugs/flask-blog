.PHONY: help
help: ## Show this help
	@egrep -h '\s##\s' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

.PHONY: venv
venv: ## Make a new virtual environment
	pipenv shell

.PHONY: install
install: venv ## Install or update dependencies
	pipenv install

freeze: ## Pin current dependencies
	pipenv run pip freeze > requirements.txt

test: ## Run the unit tests
	FLASK_APP=run.py flask test

createdb: ## Create database
	FLASK_APP=run.py flask init_db

init: ## Init database
	FLASK_APP=run.py flask db init

stamp: ## Set the revision in the database to the head, without performing any migrations.
	FLASK_APP=run.py flask db stamp head

revision: ## Revision database
	FLASK_APP=run.py flask db revision --rev-id 15dcb6d541ef

migrate: ## Generate an initial migration
	FLASK_APP=run.py flask db migrate -m 'Intial Migration'

upgrade: ## Apply the migration to the database
	FLASK_APP=run.py flask db migrate -m 'Upgrade Migration'

downgrade: ## Remove the last migration from the database
	FLASK_APP=run.py flask db downgrade

shell: ## Flask Shell Load
	FLASK_APP=run.py flask shell
