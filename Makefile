.PHONY: help start stop restart logs clean reset-db create-invitation shell-auth shell-checklist shell-knowledge shell-postgres shell-redis status full-reboot logs-notification logs-escalation logs-meeting shell-notification shell-escalation shell-meeting restart-notification restart-escalation restart-meeting reboot-notification reboot-escalation reboot-meeting logs-admin restart-admin restart-admin-dev reboot-admin shell-admin logs-telegram restart-telegram reboot-telegram shell-telegram dev-admin dev-meeting reset-locks update-deps mock-data prune test coverage coverage-html coverage-clean build-push docker-login prod-pull prod-up prod-down prod-logs prod-deploy up up-svc generate-secrets

# Docker compose project name
PROJECT_NAME = mentor-bot

help:
	@echo "=== Mentor Bot: Management Commands ==="
	@echo ""
	@echo "Main commands:"
	@echo "  make start             - Start the project (docker compose up -d --build)"
	@echo "  make up               - Start without rebuild (use after make start)"
	@echo "  make up-svc SERVICE=x - Start a single service without rebuild"
	@echo "  make stop              - Stop the project (docker compose stop)"
	@echo "  make restart           - Rebuild the entire project (down + up --build)"
	@echo "  make full-reboot       - Restart the entire project with full clean"
	@echo "  make logs              - Show logs for all services"
	@echo "  make logs-auth         - Show logs for auth service"
	@echo "  make logs-checklist    - Show logs for checklists service"
	@echo "  make logs-knowledge    - Show logs for knowledge service"
	@echo "  make logs-notification - Show logs for notification service"
	@echo "  make logs-escalation   - Show logs for escalation service"
	@echo "  make logs-meeting      - Show logs for meeting service"
	@echo "  make logs-admin        - Show logs for admin web service"
	@echo "  make logs-telegram     - Show logs for telegram bot"
	@echo "  make logs-minio        - Show logs for MinIO service"
	@echo "  make status            - Show status of all containers"
	@echo "  make status-watch      - Watch container status in real-time (updates every 1s)"
	@echo ""
	@echo "Database management:"
	@echo "  make reset-db          - Full database reset (remove volumes + build cache)"
	@echo "  make clean             - Clean project (containers, volumes, images)"
	@echo "  make reset-locks       - Delete all uv.lock files and regenerate with uv sync"
	@echo "  make update-deps       - Check PyPI and update outdated deps (uv remove/add)"
	@echo "  make prune             - Remove dangling Docker images, containers, volumes, and build cache"
	@echo "  make generate-secrets  - Generate .env from .env.example with secure random secrets"

	@echo ""
	@echo "Service access:"
	@echo "  make shell-auth        - Enter auth service container"
	@echo "  make shell-checklist   - Enter checklists service container"
	@echo "  make shell-knowledge   - Enter knowledge service container"
	@echo "  make shell-notification - Enter notification service container"
	@echo "  make shell-escalation  - Enter escalation service container"
	@echo "  make shell-meeting     - Enter meeting service container"
	@echo "  make shell-admin       - Enter admin web container"
	@echo "  make shell-telegram    - Enter telegram bot container"
	@echo "  make shell-postgres    - Enter PostgreSQL container"
	@echo "  make shell-redis       - Enter Redis container"
	@echo "  make shell-minio       - Enter MinIO container"
	@echo "  make shell-pgadmin     - Enter pgAdmin container"
	@echo ""
	@echo "Service restart (down + up --build):"
	@echo "  make restart-auth      - Rebuild auth service"
	@echo "  make restart-checklist - Rebuild checklists service"
	@echo "  make restart-knowledge - Rebuild knowledge service"
	@echo "  make restart-notification - Rebuild notification service"
	@echo "  make restart-escalation - Rebuild escalation service"
	@echo "  make restart-meeting   - Rebuild meeting service"
	@echo "  make restart-admin     - Rebuild admin web service"
	@echo "  make restart-telegram  - Rebuild telegram bot"
	@echo ""
	@echo "Service reboot (quick restart, no rebuild):"
	@echo "  make reboot-auth       - Quick restart auth service"
	@echo "  make reboot-checklist  - Quick restart checklists service"
	@echo "  make reboot-knowledge  - Quick restart knowledge service"
	@echo "  make reboot-notification - Quick restart notification service"
	@echo "  make reboot-escalation - Quick restart escalation service"
	@echo "  make reboot-meeting    - Quick restart meeting service"
	@echo "  make reboot-admin      - Quick restart admin web service"
	@echo "  make reboot-telegram   - Quick restart telegram bot"
	@echo ""
	@echo "Testing:"
	@echo "  make test              - Run all unit tests across all Python services"
	@echo "  make test-admin        - Run admin_web unit tests (Vitest)"
	@echo "  make test-admin-coverage - Run admin_web tests with coverage"
	@echo "  make test-admin-watch  - Run admin_web tests in watch mode"
	@echo "  make coverage          - Run tests, generate reports, and serve unified dashboard"
	@echo "  make coverage-serve    - Serve existing coverage reports (skip test run)"
	@echo "  make coverage-html     - Show coverage report URL"
	@echo "  make coverage-clean    - Remove all coverage reports"
	@echo ""
	@echo "Production deploy:"
	@echo "  DOCKER_USERNAME=user make build-push [TAG=sha]  - Build & push all images"
	@echo "  make docker-login DOCKER_USERNAME=user          - Login to Docker Hub"
	@echo "  make prod-pull                                  - Pull prod images on VPS"
	@echo "  make prod-up / prod-down / prod-logs            - Manage prod stack"
	@echo "  make prod-deploy                                - Pull + up in one step"
	@echo ""

test:
	@python scripts/run_tests.py

coverage:
	@echo "Running tests with coverage across all services..."
	@mkdir -p .coverage-reports
	@for svc in auth_service checklists_service escalation_service feedback_service knowledge_service meeting_service notification_service telegram_bot; do \
		if [ ! -d "$$svc/tests" ]; then \
			echo "=== $$svc (no tests, skipping) ==="; \
		else \
			echo "=== $$svc ===" && \
			(cd "$$svc" && env -u VIRTUAL_ENV uv run pytest tests/ \
				--cov="$$svc" \
				--cov-report=term-missing:skip-covered \
				--cov-report=xml:../.coverage-reports/$$svc.xml \
				--cov-report=html:../.coverage-reports/$$svc-html \
				-q) || true; \
		fi; \
	done
	@echo ""
	@python scripts/aggregate_coverage.py

coverage-serve:
	@python scripts/serve_coverage.py

coverage-html:
	@echo "Coverage reports are served at http://localhost:8765"
	@echo "Run 'make coverage-serve' to start the server, or 'make coverage' to regenerate and serve"

coverage-clean:
	rm -rf .coverage-reports
	@echo "Coverage reports cleaned"

test-admin:
	cd admin_web && bunx vitest run

test-admin-coverage:
	cd admin_web && bun run test:coverage

test-admin-watch:
	cd admin_web && bun run test:watch

start:
	docker compose up -d --build

up:
	docker compose up -d

up-svc:
	@if [ -z "$(SERVICE)" ]; then echo "SERVICE is required (e.g. SERVICE=auth_service)"; exit 1; fi
	docker compose up -d $(SERVICE)

prune:
	docker image prune -f
	docker container prune -f
	docker volume prune -f
	docker builder prune -f
	@echo "Dangling images, containers, volumes, and build cache removed"

full-reboot: reset-db start mock-data

mock-data: 
	python ./scripts/setup_mock_data.py
stop:
	docker compose stop

restart:
	docker compose down
	docker compose up -d --build

restart-auth:
	docker compose stop auth_service && docker compose up -d --build auth_service

restart-checklist:
	docker compose stop checklists_service && docker compose up -d --build checklists_service

restart-knowledge:
	docker compose stop knowledge_service && docker compose up -d --build knowledge_service

restart-notification:
	docker compose stop notification_service && docker compose up -d --build notification_service

restart-escalation:
	docker compose stop escalation_service && docker compose up -d --build escalation_service

restart-meeting:
	docker compose stop meeting_service && docker compose up -d --build meeting_service

restart-admin:
	docker compose stop admin_web && docker compose up -d --build admin_web

restart-admin-dev:
	docker compose stop admin_web && docker compose up -d --build admin_web

restart-telegram:
	docker compose stop telegram_bot && docker compose up -d --build telegram_bot

reboot-auth:
	docker compose restart auth_service

reboot-checklist:
	docker compose restart checklists_service

reboot-knowledge:
	docker compose restart knowledge_service

reboot-notification:
	docker compose restart notification_service

reboot-escalation:
	docker compose restart escalation_service

reboot-meeting:
	docker compose restart meeting_service

reboot-admin:
	docker compose restart admin_web

reboot-telegram:
	docker compose restart telegram_bot

logs:
	docker compose logs -f auth_service checklists_service knowledge_service notification_service escalation_service meeting_service feedback_service telegram_bot admin_web

logs-auth:
	docker compose logs -f auth_service

logs-checklist:
	docker compose logs -f checklists_service

logs-knowledge:
	docker compose logs -f knowledge_service

logs-notification:
	docker compose logs -f notification_service

logs-escalation:
	docker compose logs -f escalation_service

logs-meeting:
	docker compose logs -f meeting_service

logs-admin:
	docker compose logs -f admin_web

logs-telegram:
	docker compose logs -f telegram_bot

logs-minio:
	docker compose logs -f minio

status:
	docker compose ps --format "table {{.Name}}\t{{.Status}}"

status-watch:
	watch -n 1 "docker compose ps --format 'table {{.Name}}\t{{.Status}}'"

shell-auth:
	docker compose exec auth_service /bin/bash

shell-checklist:
	docker compose exec checklists_service /bin/bash

shell-knowledge:
	docker compose exec knowledge_service /bin/bash

shell-notification:
	docker compose exec notification_service /bin/bash

shell-escalation:
	docker compose exec escalation_service /bin/bash

shell-meeting:
	docker compose exec meeting_service /bin/bash

shell-admin:
	docker compose exec admin_web /bin/sh

shell-telegram:
	docker compose exec telegram_bot sh

shell-postgres:
	docker compose exec postgres psql -U ${POSTGRES_USER:-postgres} -d ${POSTGRES_DB:-mentor_bot}

shell-redis:
	docker compose exec redis redis-cli

shell-minio:
	docker compose exec minio sh

shell-pgadmin:
	docker compose exec pgadmin /bin/bash

reset-db:
	docker compose down
	@echo "Removing volumes and build cache..."
	@if docker volume ls | grep -q "${PROJECT_NAME}_postgres_data"; then \
		docker volume rm ${PROJECT_NAME}_postgres_data; \
		echo "Removed postgres_data volume"; \
	fi
	@if docker volume ls | grep -q "${PROJECT_NAME}_redis_data"; then \
		docker volume rm ${PROJECT_NAME}_redis_data; \
		echo "Removed redis_data volume"; \
	fi
	docker builder prune -f
	@echo "Removed Docker build cache"
# 	@if docker volume ls | grep -q "${PROJECT_NAME}_pgadmin-data"; then \
# 		docker volume rm ${PROJECT_NAME}_pgadmin-data; \
# 		echo "Removed pgadmin-data volume"; \
# 	fi
# 	@if docker volume ls | grep -q "${PROJECT_NAME}_redis-insight"; then \
# 		docker volume rm ${PROJECT_NAME}_redis-insight; \
# 		echo "Removed redis-insight volume"; \
# 	fi

clean:
	docker compose down -v --rmi all --remove-orphans
	@echo "Project cleaned successfully"

reset-locks:
	@for dir in auth_service checklists_service knowledge_service notification_service escalation_service feedback_service meeting_service telegram_bot; do \
		echo "Rebuilding $$dir..."; \
		rm -f $$dir/uv.lock; \
		env -u VIRTUAL_ENV uv sync --directory $$dir; \
	done
	@echo "All uv.lock files rebuilt"

update-deps:
	python scripts/update_deps.py

generate-env:
	@if [ -f .env ]; then \
		read -p ".env already exists. Overwrite? (y/N) " -n 1 -r; \
		echo; \
		if [[ ! $$REPLY =~ ^[Yy]$$ ]]; then \
			echo "Aborted."; \
			exit 1; \
		fi; \
	fi
	python scripts/generate_env.py



# Health check commands
health:
	@echo "Checking service health..."
	@echo "Auth Service: $$(docker compose exec auth_service curl -s -o /dev/null -w '%{http_code}' http://localhost:8000/health)"
	@echo "Checklists Service: $$(docker compose exec checklists_service curl -s -o /dev/null -w '%{http_code}' http://localhost:8000/health)"
	@echo "Knowledge Service: $$(docker compose exec knowledge_service curl -s -o /dev/null -w '%{http_code}' http://localhost:8000/health)"
	@echo "Notification Service: $$(docker compose exec notification_service curl -s -o /dev/null -w '%{http_code}' http://localhost:8000/health)"
	@echo "Escalation Service: $$(docker compose exec escalation_service curl -s -o /dev/null -w '%{http_code}' http://localhost:8000/health)"
	@echo "Meeting Service: $$(docker compose exec meeting_service curl -s -o /dev/null -w '%{http_code}' http://localhost:8000/health)"
	@echo "Admin Web: $$(docker compose exec admin_web wget -q -O /dev/null -S 'http://localhost:3000/' 2>&1 | head -1 | awk '{print $$2}' || echo 'unhealthy')"
	@echo "PostgreSQL: $$(docker compose exec postgres pg_isready -U ${POSTGRES_USER:-postgres} -d ${POSTGRES_DB:-mentor_bot} >/dev/null 2>&1 && echo 'healthy' || echo 'unhealthy')"
	@echo "Redis: $$(docker compose exec redis redis-cli ping | grep -q PONG && echo 'healthy' || echo 'unhealthy')"

# Development commands
dev-auth:
	docker compose up -d postgres redis
	docker compose logs -f auth_service

dev-checklist:
	docker compose up -d postgres redis auth_service
	docker compose logs -f checklists_service

dev-knowledge:
	docker compose up -d postgres redis auth_service
	docker compose logs -f knowledge_service

dev-meeting:
	docker compose up -d postgres redis auth_service
	docker compose logs -f meeting_service

dev-admin:
	docker compose up -d postgres redis auth_service checklists_service knowledge_service notification_service escalation_service meeting_service feedback_service
	cd admin_web && bun install && bun dev

# Database backup/restore commands
backup-db:
	@mkdir -p backups
	docker compose exec postgres pg_dump -U ${POSTGRES_USER:-postgres} ${POSTGRES_DB:-mentor_bot} > backups/backup_$(shell date +%Y%m%d_%H%M%S).sql
	@echo "Database backup created in backups/ directory"

restore-db:
	@if [ -z "$(FILE)" ]; then \
		echo "Usage: make restore-db FILE=backups/backup_file.sql"; \
	else \
		docker compose exec -T postgres psql -U ${POSTGRES_USER:-postgres} -d ${POSTGRES_DB:-mentor_bot} < $(FILE); \
		echo "Database restored from $(FILE)"; \
	fi

# ─── Production: build/push images and deploy ────────────────────────────────
# Usage:
#   DOCKER_USERNAME=youruser make build-push              # tag = git short SHA
#   DOCKER_USERNAME=youruser TAG=v1.2.3 make build-push
#
# On the VPS (.env must define DOCKER_USERNAME and IMAGE_TAG):
#   make prod-pull && make prod-up
#   make prod-deploy TAG=<sha>     # pull + up in one step

PROD_COMPOSE = docker compose -f docker-compose.prod.yml

docker-login:
	@if [ -z "$(DOCKER_USERNAME)" ]; then echo "DOCKER_USERNAME is required"; exit 1; fi
	docker login -u $(DOCKER_USERNAME)

build-push:
	@if [ -z "$(DOCKER_USERNAME)" ]; then echo "DOCKER_USERNAME is required"; exit 1; fi
	DOCKER_USERNAME=$(DOCKER_USERNAME) ./scripts/build-and-push.sh $(TAG)

prod-pull:
	$(PROD_COMPOSE) pull

prod-up:
	$(PROD_COMPOSE) up -d

prod-down:
	$(PROD_COMPOSE) down

prod-logs:
	$(PROD_COMPOSE) logs -f

prod-deploy:
	$(PROD_COMPOSE) down
	$(PROD_COMPOSE) pull
	$(PROD_COMPOSE) up -d
	$(PROD_COMPOSE) ps

# ─── Alembic migrations ───────────────────────────────────────────────────────
# SERVICE: one of auth_service checklists_service knowledge_service
#          notification_service escalation_service feedback_service meeting_service
# MSG:     migration message (required for migrate-revision)
#
# Examples:
#   make migrate-revision SERVICE=auth_service MSG="add user avatar column"
#   make migrate-upgrade SERVICE=auth_service
#   make migrate-current SERVICE=auth_service
#   make migrate-history SERVICE=auth_service
#   make migrate-all        # upgrade head on every DB service

DB_SERVICES = auth_service checklists_service knowledge_service \
              notification_service escalation_service feedback_service meeting_service

_check-service:
	@if [ -z "$(SERVICE)" ]; then echo "SERVICE is required (e.g. SERVICE=auth_service)"; exit 1; fi

migrate-revision: _check-service
	@if [ -z "$(MSG)" ]; then echo "MSG is required (e.g. MSG=\"add column\")"; exit 1; fi
	cd $(SERVICE) && uv run alembic revision --autogenerate -m "$(MSG)"

migrate-upgrade: _check-service
	cd $(SERVICE) && uv run alembic upgrade head

migrate-downgrade: _check-service
	@if [ -z "$(REV)" ]; then echo "REV is required (e.g. REV=-1 or REV=abc123)"; exit 1; fi
	cd $(SERVICE) && uv run alembic downgrade $(REV)

migrate-current: _check-service
	cd $(SERVICE) && uv run alembic current

migrate-history: _check-service
	cd $(SERVICE) && uv run alembic history --verbose

migrate-stamp: _check-service
	@if [ -z "$(REV)" ]; then REV=head; fi
	cd $(SERVICE) && uv run alembic stamp $${REV:-head}

migrate-all:
	@for svc in $(DB_SERVICES); do \
		echo ">>> Upgrading $$svc"; \
		(cd $$svc && uv run alembic upgrade head) || exit 1; \
	done
	@echo "All migrations applied."
