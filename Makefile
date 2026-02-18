# ==============================================================================
# Trivivo Makefile
# ==============================================================================
# Django project automation for development, testing, and database management.
#
# Usage:
#   make help       - Show this help message
#   make setup      - Complete one-time setup
#   make run        - Start development server
#
# ==============================================================================

# ------------------------------------------------------------------------------
# Configuration
# ------------------------------------------------------------------------------
SHELL := /bin/bash
.DEFAULT_GOAL := help

# Project paths
PROJECT_ROOT := $(shell pwd)
VENV_DIR := $(PROJECT_ROOT)/.venv
TAILWIND_SRC := $(PROJECT_ROOT)/tailwind_theme/static_src
DB_FILE := $(PROJECT_ROOT)/db.sqlite3

# Python/Django commands (using uv)
UV := uv
PYTHON := $(UV) run python
MANAGE := $(UV) run python manage.py

# Migration directories for cleanup
MIGRATION_DIRS := game/migrations adminpanel/migrations auth/migrations

# Colors for output
YELLOW := \033[1;33m
GREEN := \033[1;32m
RED := \033[1;31m
CYAN := \033[1;36m
NC := \033[0m

# ------------------------------------------------------------------------------
# Help
# ------------------------------------------------------------------------------
.PHONY: help
help: ## Show this help message
	@printf "$(CYAN)Trivivo - Django Project Commands$(NC)\n"
	@printf "\n"
	@printf "$(GREEN)Primary Commands:$(NC)\n"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  $(YELLOW)%-20s$(NC) %s\n", $$1, $$2}'
	@printf "\n"
	@printf "$(RED)Destructive Commands (use with caution):$(NC)\n"
	@grep -E '^[a-zA-Z_-]+:.*?##! .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?##! "}; {printf "  $(YELLOW)%-20s$(NC) %s\n", $$1, $$2}'

# ------------------------------------------------------------------------------
# Primary Development Commands
# ------------------------------------------------------------------------------
.PHONY: setup run run-server run-tailwind check test test-failed

setup: _check-requirements ## Complete one-time setup: venv, deps, tailwind, migrate
	@printf "$(CYAN)>>> Setting up Trivivo development environment...$(NC)\n"
	$(UV) venv --seed
	$(UV) pip install -e ".[dev]"
	@printf "$(CYAN)>>> Installing Tailwind dependencies...$(NC)\n"
	cd $(TAILWIND_SRC) && npm install
	@printf "$(CYAN)>>> Running database migrations...$(NC)\n"
	$(MAKE) migrate
	@printf "$(GREEN)>>> Setup complete! Run 'make run' to start the server.$(NC)\n"

run: ## Start Django development server with Tailwind
	@printf "$(CYAN)>>> Starting development server...$(NC)\n"
	@trap 'kill %1 2>/dev/null' EXIT; \
		$(MANAGE) tailwind start & \
		$(MANAGE) runserver

run-server: ## Start Django development server only (no Tailwind)
	$(MANAGE) runserver

run-tailwind: ## Start Tailwind CSS watcher only
	$(MANAGE) tailwind start

check: format lint ## Run all code quality checks (format, lint)
	@printf "$(CYAN)>>> Running Django system checks...$(NC)\n"
	$(MANAGE) check
	@printf "$(GREEN)>>> All checks passed!$(NC)\n"

test: ## Run pytest test suite with coverage reporting
	@printf "$(CYAN)>>> Running tests with coverage...$(NC)\n"
	source .env && $(UV) run pytest --cov=. --cov-report=term-missing --cov-report=html

test-failed: ## Re-run only failed tests
	@printf "$(CYAN)>>> Re-running failed tests...$(NC)\n"
	source .env && $(UV) run pytest --lf

# ------------------------------------------------------------------------------
# Code Quality & Formatting
# ------------------------------------------------------------------------------
.PHONY: format lint

format: ## Auto-format code with ruff
	@printf "$(CYAN)>>> Formatting code with ruff...$(NC)\n"
	$(UV) run ruff format .

lint: ## Run linting with ruff (auto-fixes issues)
	@printf "$(CYAN)>>> Linting code with ruff...$(NC)\n"
	$(UV) run ruff check --fix .

# ------------------------------------------------------------------------------
# Database Management
# ------------------------------------------------------------------------------
.PHONY: migrations migrate bootstrap seed shell dbshell

migrations: ## Create new Django migrations
	@printf "$(CYAN)>>> Creating migrations...$(NC)\n"
	$(MANAGE) makemigrations

migrate: ## Apply pending migrations
	@printf "$(CYAN)>>> Applying migrations...$(NC)\n"
	$(MANAGE) migrate

bootstrap: ## Initialize database with base data (categories, levels, lifelines)
	@printf "$(CYAN)>>> Bootstrapping database with base data...$(NC)\n"
	$(MANAGE) createcategories
	$(MANAGE) createlevels
	$(MANAGE) createlifelines
	@printf "$(GREEN)>>> Bootstrap complete!$(NC)\n"

seed: ## Populate database with test data from OpenTriviaDB
	@printf "$(CYAN)>>> Seeding database with questions...$(NC)\n"
	@FILE_NAME=$$($(MANAGE) fetchqns 10) && \
		printf "$(CYAN)>>> Fetched questions to: $$FILE_NAME$(NC)\n" && \
		$(MANAGE) extractoptions $$FILE_NAME && \
		$(MANAGE) addquestions $$FILE_NAME && \
		rm -f $$FILE_NAME && \
		printf "$(GREEN)>>> Seed complete!$(NC)\n"

shell: ## Open Django shell
	$(MANAGE) shell

dbshell: ## Open database shell
	$(MANAGE) dbshell

# ------------------------------------------------------------------------------
# Destructive Commands
# ------------------------------------------------------------------------------
.PHONY: nuke-db restart _confirm-destructive

_confirm-destructive:
	@printf "$(RED)>>> WARNING: This is a destructive operation!$(NC)\n"
	@read -p "Are you sure you want to continue? [y/N] " confirm && \
		[ "$$confirm" = "y" ] || [ "$$confirm" = "Y" ] || \
		(printf "$(YELLOW)>>> Aborted.$(NC)\n" && exit 1)

nuke-db: _confirm-destructive ##! DESTRUCTIVE: Delete database and migration files
	@printf "$(RED)>>> Nuking database and migrations...$(NC)\n"
	rm -f $(DB_FILE)
	@for dir in $(MIGRATION_DIRS); do \
		find $$dir -type f -name '*.py' ! -name '__init__.py' -delete 2>/dev/null || true; \
		printf "$(YELLOW)>>> Cleaned migrations in $$dir$(NC)\n"; \
	done
	@printf "$(GREEN)>>> Database and migrations deleted. Run 'make migrate' to recreate.$(NC)\n"

restart: _confirm-destructive ##! DESTRUCTIVE: Full restart (nuke db, migrate, bootstrap)
	@printf "$(RED)>>> Performing full restart...$(NC)\n"
	rm -f $(DB_FILE)
	@for dir in $(MIGRATION_DIRS); do \
		find $$dir -type f -name '*.py' ! -name '__init__.py' -delete 2>/dev/null || true; \
	done
	$(MAKE) migrate
	$(MAKE) bootstrap
	@printf "$(GREEN)>>> Restart complete!$(NC)\n"

# ------------------------------------------------------------------------------
# Testing Variants
# ------------------------------------------------------------------------------
.PHONY: test-functional test-pipeline

test-functional: ## Run functional tests only
	@printf "$(CYAN)>>> Running functional tests...$(NC)\n"
	source .env && $(UV) run pytest tests/functional/ -v

test-pipeline: ## Run tests with 100% coverage requirement (for CI)
	@printf "$(CYAN)>>> Running pipeline tests with strict coverage...$(NC)\n"
	source .env && $(UV) run pytest --cov=. --cov-report=term-missing --cov-fail-under=100

# ------------------------------------------------------------------------------
# Utility Commands
# ------------------------------------------------------------------------------
.PHONY: clean superuser collectstatic _check-requirements

clean: ## Clean up temporary files and caches
	@printf "$(CYAN)>>> Cleaning up...$(NC)\n"
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	find . -type f -name ".coverage" -delete 2>/dev/null || true
	rm -rf .pytest_cache htmlcov .mypy_cache .ruff_cache
	@printf "$(GREEN)>>> Cleanup complete!$(NC)\n"

superuser: ## Create a Django superuser
	$(MANAGE) createsuperuser

collectstatic: ## Collect static files for production
	$(MANAGE) collectstatic --noinput

_check-requirements:
	@command -v uv >/dev/null 2>&1 || \
		(printf "$(RED)Error: 'uv' is not installed. Install it with: curl -LsSf https://astral.sh/uv/install.sh | sh$(NC)\n" && exit 1)
	@command -v npm >/dev/null 2>&1 || \
		(printf "$(RED)Error: 'npm' is not installed. Please install Node.js.$(NC)\n" && exit 1)
