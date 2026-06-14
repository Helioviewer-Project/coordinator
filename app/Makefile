UID := $(shell id -u)
GID := $(shell id -g)

# Run docker compose with this instance's nginx-proxy / Let's Encrypt settings
# loaded from app/.env (copy app/.env.example to app/.env and edit it).
# UID/GID are passed via the shell environment so they take precedence over
# anything in the env-file.
DOCKER_COMPOSE := UID=$(UID) GID=$(GID) docker compose --env-file .env

.PHONY: deploy up up-d down logs status build test shell format lint check help

.DEFAULT_GOAL := help

help: ## Show this help message
	@echo "Usage: make [target]"
	@echo ""
	@echo "  First run:  cp .env.example .env   # then edit your domain/email"
	@echo "  Deploy:     make deploy            # run on your VIRTUAL_HOST via nginx-proxy"
	@echo ""
	@echo "Targets:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  %-15s %s\n", $$1, $$2}'

# Create app/.env from the template on first run (gitignored, holds your values).
.env:
	@cp .env.example .env
	@echo ">> Created app/.env from .env.example."
	@echo ">> Edit it with your VIRTUAL_HOST / LETSENCRYPT_HOST / LETSENCRYPT_EMAIL, then re-run."
	@exit 1

deploy: .env ## Build + run on your domain behind nginx-proxy (detached)
	$(DOCKER_COMPOSE) up --build -d
	@host=$$(grep -E '^VIRTUAL_HOST=' .env | cut -d= -f2); \
	 echo ""; \
	 echo "Coordinator is starting behind nginx-proxy:"; \
	 echo "  https://$$host"; \
	 echo "  https://$$host/health-check"; \
	 echo "Use 'make logs' to follow startup and 'make status' to check health."

up: .env ## Start the app with docker compose (foreground)
	$(DOCKER_COMPOSE) up --build

up-d: deploy ## Alias for 'deploy' (start detached)

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

lint: .env ## Check code style with black and flake8
	$(DOCKER_COMPOSE) run --rm app -m black --check .
	$(DOCKER_COMPOSE) run --rm app -m flake8 --exclude=test .

check: lint test ## Run all checks (lint + test)
