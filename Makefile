# Makefile for Library Service

# --- Environment variables ---
DOCKER_COMPOSE = docker compose
DJANGO_CONTAINER = django-web

# --- Commands ---
init:   ## Copy .env and build containers
	@cp .env.sample .env
	@$(DOCKER_COMPOSE) build

migrate:    ## Make migrations in Django
	@$(DOCKER_COMPOSE) run --rm $(DJANGO_CONTAINER) python manage.py migrate

run:    ## Run all containers in background
	@$(DOCKER_COMPOSE) up -d

setup: init migrate run ## Complete setup

tests:  ## Run tests in Django
	@$(DOCKER_COMPOSE) run --rm $(DJANGO_CONTAINER) pytest

stop:   ## Stops all containers
	@$(DOCKER_COMPOSE) down

logs:   ## Show logs of Django container
	@$(DOCKER_COMPOSE) logs -f $(DJANGO_CONTAINER)

help:  ## Show this help message
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
	awk 'BEGIN {FS = ":.*?## "}; {printf "  %-10s %s\n", $$1, $$2}'
