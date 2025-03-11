APP_VERSION=$(shell docker-compose run app poetry version --short)
INSTALLER_FILE_NAME="alinka-$(APP_VERSION).deb"

.PHONY: build

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'


test: ## Run all unit tests
	docker-compose -f docker-compose.test.yml run --rm app pytest

name=
test-case: ## Run single test unit
	docker-compose -f docker-compose.test.yml run --rm app pytest -k ${name}

build: ## Build docker image
	docker-compose build --no-cache

run: ## Run application
	docker-compose up

type=specjalne
generate: ## Generate documents. Use `type=` params to create given type of document.
	docker-compose run --rm app python alinka/create_documents.py --type ${type}

populate_schools: ## Populate school db table with fixtures
	docker-compose run app python alinka/scripts.py

style: ## Run black, isort, flake8 linters
	docker-compose run --rm app bash -c "black . && isort . && flake8 ."

style-check:
	docker-compose run --rm app bash -c "black . --check && isort . --check && flake8 ."

installer: ## Create installer
	docker-compose run --rm -u root app rm -rf dist/ build/ package/ $(INSTALLER_FILE_NAME)
	docker-compose run --rm -u root app pyinstaller alinka.spec --noconfirm
	docker-compose run --rm -u root app ./package.sh
	docker-compose run --rm -u root app fpm -v $(APP_VERSION) -p $(INSTALLER_FILE_NAME)

installer-name: ## Display name of installer of current version of app
	@echo $(INSTALLER_FILE_NAME)

bash:
	docker compose run --rm app bash

message=auto
create-migration: ## Generate migration. Add `message` to migration, ie. `make create-migration message=my_message`
	docker compose run --rm app bash -c "alembic revision --autogenerate -m \"$(message)\""

migrate:
	docker compose run --rm app bash -c "alembic upgrade head"
