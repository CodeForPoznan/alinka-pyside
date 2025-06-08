APP_VERSION=$(shell date +"%Y.%m.%d")-$(shell git rev-parse --short HEAD)
INSTALLER_FILE_NAME="alinka-$(APP_VERSION).deb"

.PHONY: build

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

test: ## Run all unit tests
	docker compose -f docker-compose.test.yml run --rm app pytest

name=
test-case: ## Run single test unit
	docker compose -f docker-compose.test.yml run --rm app pytest -k ${name}

build: ## Build docker image
	docker compose build

run: ## Run application
	docker compose up

type=specjalne
create_documents: ## Create documents. Use `type=` params to create given type of document.
	docker compose run --rm app python tools/create_documents.py --type ${type}

populate_database: ## Populate DB tables using factories
	docker compose run app python tools/populate_database.py

style: ## Run black, isort, flake8 linters
	docker compose run --rm app bash -c "black . && isort . && flake8 ."

style-check:
	docker compose run --rm app bash -c "black . --check && isort . --check && flake8 ."

installer: ## Create installer
	docker compose run --rm -u root app rm -rf dist/ build/ package/ $(INSTALLER_FILE_NAME)
	docker compose run --rm -u root app pyinstaller alinka.spec --noconfirm
	docker compose run --rm -u root app ./package.sh
	docker compose run --rm -u root app fpm -v $(APP_VERSION) -p $(INSTALLER_FILE_NAME)

# This is theoretical list definition
# it hasn't been run even once yet, as I don't have Make installed on my Windows VM
win-installer:
#	as installing CairoSVG is nontrivial for time being I run it once and
#	commiting ICO format to git repository
#	poetry run python .\tools\svg_to_ico.py .\statics\alinka.svg .\statics\alinka.ico
	poetry run pyinstaller alinka.spec --noconfirm
# to run iscc you need to install Inno Setup 6 (see: https://jrsoftware.org/isdl.php)
	ISCC.exe /DAppVersion="$(APP_VERSION)" .\installer.iss

get-app-version:
	@echo $(APP_VERSION)

installer-name: ## Display name of installer of current version of app
	@echo $(INSTALLER_FILE_NAME)

bash:
	docker compose run --rm app bash

message=auto
create-migration: ## Generate migration. Add `message` to migration, ie. `make create-migration message=my_message`
	docker compose run --rm app bash -c "alembic revision --autogenerate -m \"$(message)\""

check-migrations:
	docker compose run --rm app bash -c "alembic upgrade head && alembic check"
