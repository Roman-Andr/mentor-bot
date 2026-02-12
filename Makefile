.PHONY: help start stop restart logs clean reset-db create-invitation shell-auth shell-checklist shell-knowledge shell-postgres shell-redis status full-reboot logs-notification logs-escalation shell-notification shell-escalation restart-notification restart-escalation

# Docker compose project name
PROJECT_NAME = mentor-bot

help:
	@echo "=== Mentor Bot: Management Commands ==="
	@echo ""
	@echo "Main commands:"
	@echo "  make start             - Start the project (docker compose up -d --build)"
	@echo "  make stop              - Stop the project (docker compose stop)"
	@echo "  make restart           - Restart the entire project"
	@echo "  make full-reboot       - Restart the entire project with full clean"
	@echo "  make logs              - Show logs for all services"
	@echo "  make logs-auth         - Show logs for auth service"
	@echo "  make logs-checklist    - Show logs for checklists service"
	@echo "  make logs-knowledge    - Show logs for knowledge service"
	@echo "  make logs-notification - Show logs for notification service"
	@echo "  make logs-escalation   - Show logs for escalation service"
	@echo "  make status            - Show status of all containers"
	@echo ""
	@echo "Database management:"
	@echo "  make reset-db          - Full database reset (remove volume)"
	@echo "  make clean             - Clean project (containers, volumes, images)"
	@echo ""
	@echo "Service access:"
	@echo "  make shell-auth        - Enter auth service container"
	@echo "  make shell-checklist   - Enter checklists service container"
	@echo "  make shell-knowledge   - Enter knowledge service container"
	@echo "  make shell-notification - Enter notification service container"
	@echo "  make shell-escalation  - Enter escalation service container"
	@echo "  make shell-postgres    - Enter PostgreSQL container"
	@echo "  make shell-redis       - Enter Redis container"
	@echo "  make shell-pgadmin     - Enter pgAdmin container"
	@echo ""
	@echo "Service restart:"
	@echo "  make restart-auth      - Restart auth service"
	@echo "  make restart-checklist - Restart checklists service"
	@echo "  make restart-knowledge - Restart knowledge service"
	@echo "  make restart-notification - Restart notification service"
	@echo "  make restart-escalation - Restart escalation service"
	@echo ""

start:
	docker compose up -d --build

full-reboot: reset-db start
	./scripts/create_admin.sh
	sleep 1
	./scripts/create_hr.sh
	sleep 1
	./scripts/create_user.sh
	sleep 1
	./scripts/create_checklist.sh 
	sleep 1
	./scripts/create_invitation.sh 
	sleep 1
	./scripts/test_knowledge_service.sh 

stop:
	docker compose stop

restart: stop start

restart-auth:
	docker compose restart auth_service

restart-checklist:
	docker compose restart checklists_service

restart-knowledge:
	docker compose restart knowledge_service

restart-notification:
	docker compose restart notification_service

restart-escalation:
	docker compose restart escalation_service

logs:
	docker compose logs -f

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

status:
	docker compose ps

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

shell-postgres:
	docker compose exec postgres psql -U ${POSTGRES_USER:-postgres} -d ${POSTGRES_DB:-mentor_bot}

shell-redis:
	docker compose exec redis redis-cli

shell-pgadmin:
	docker compose exec pgadmin /bin/bash

reset-db:
	docker compose down
	@echo "Removing volumes..."
	@if docker volume ls | grep -q "${PROJECT_NAME}_postgres_data"; then \
		docker volume rm ${PROJECT_NAME}_postgres_data; \
		echo "Removed postgres_data volume"; \
	fi
	@if docker volume ls | grep -q "${PROJECT_NAME}_redis_data"; then \
		docker volume rm ${PROJECT_NAME}_redis_data; \
		echo "Removed redis_data volume"; \
	fi
	@if docker volume ls | grep -q "${PROJECT_NAME}_knowledge_files"; then \
		docker volume rm ${PROJECT_NAME}_knowledge_files; \
		echo "Removed knowledge_files volume"; \
	fi
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

# Health check commands
health:
	@echo "Checking service health..."
	@echo "Auth Service: $$(docker compose exec auth_service curl -s -o /dev/null -w '%{http_code}' http://localhost:8000/health)"
	@echo "Checklists Service: $$(docker compose exec checklists_service curl -s -o /dev/null -w '%{http_code}' http://localhost:8000/health)"
	@echo "Knowledge Service: $$(docker compose exec knowledge_service curl -s -o /dev/null -w '%{http_code}' http://localhost:8000/health)"
	@echo "Notification Service: $$(docker compose exec notification_service curl -s -o /dev/null -w '%{http_code}' http://localhost:8000/health)"
	@echo "Escalation Service: $$(docker compose exec escalation_service curl -s -o /dev/null -w '%{http_code}' http://localhost:8000/health)"
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