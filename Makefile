UID := $(shell id -u)
GID := $(shell id -g)

# Run docker compose with this instance's nginx-proxy / Let's Encrypt settings
# loaded from .env (copy .env.example to .env and edit it).
# UID/GID are passed via the shell environment so they take precedence over
# anything in the env-file.
DOCKER_COMPOSE := UID=$(UID) GID=$(GID) docker compose -f docker/docker-compose.yml --env-file .env

.PHONY: up down logs status build test shell format lint check help

.DEFAULT_GOAL := help

help: ## Show this help message
	@echo "Usage: make [target]"
	@echo ""
	@echo "  First run:  cp .env.example .env   # then edit your domain/email"
	@echo "  Run:        make up                # start on your VIRTUAL_HOST via nginx-proxy"
	@echo ""
	@echo "Targets:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  %-15s %s\n", $$1, $$2}'

# Create .env from the template on first run (gitignored, holds your values).
.env:
	@cp .env.example .env
	@echo ">> Created .env from .env.example."
	@echo ">> Edit it with your VIRTUAL_HOST / LETSENCRYPT_HOST / LETSENCRYPT_EMAIL, then re-run."
	@exit 1

up: .env ## Start the app with docker compose (foreground)
	$(DOCKER_COMPOSE) up --build

down: ## Stop the app
	$(DOCKER_COMPOSE) down

logs: ## Follow the app logs
	$(DOCKER_COMPOSE) logs -f

status: ## Show container status / health
	$(DOCKER_COMPOSE) ps

build: .env ## Build the docker image
	$(DOCKER_COMPOSE) build

test: .env ## Run pytest in docker
	$(DOCKER_COMPOSE) run --rm app -m pytest test/ -v

shell: .env ## Open a bash shell in the container
	$(DOCKER_COMPOSE) run --rm --entrypoint /bin/bash app

format: .env ## Format code with black
	$(DOCKER_COMPOSE) run --rm app -m black .

lint: .env ## Check code style with flake8 and black
	$(DOCKER_COMPOSE) run --rm app -m flake8 --ignore=E501
	$(DOCKER_COMPOSE) run --rm app -m black --check .

check: lint test ## Run all checks (lint + test)
