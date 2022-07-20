MANAGE := FLASK_APP=run.py


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
	pipenv run pip freeze --local > requirements.txt

test: ## Run the unit tests
	$(MANAGE) flask test

createdb: ## Create database
	$(MANAGE) flask init_db

init: ## Init database
	$(MANAGE) flask db init

stamp: ## Set the revision in the database to the head, without performing any migrations.
	$(MANAGE) flask db stamp head

revision: ## Revision database
	$(MANAGE) flask db revision --rev-id 15dcb6d541ef

migrate: ## Generate an initial migration
	$(MANAGE) flask db migrate -m 'Intial Migration'

upgrade: ## Apply the migration to the database
	$(MANAGE) flask db migrate -m 'Upgrade Migration'

downgrade: ## Remove the last migration from the database
	$(MANAGE) flask db downgrade

shell: ## Flask Shell Load
	$(MANAGE) flask shell

create-db-backup: ## create backup database
	$(MANAGE) flask alchemydumps create

create-db-restore: ## restore backup database
	$(MANAGE) flask alchemydumps restore -d

create-db-remove: ## remove backup database
	$(MANAGE) flask alchemydumps remove -d

create-db-autoclean: ## autoclean backup database
	$(MANAGE) flask alchemydumps autoclean
