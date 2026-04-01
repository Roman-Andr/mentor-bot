#!/usr/bin/env python3
"""
Mock Data Setup Script for Mentor Bot

Creates test data across all microservices using JSON configuration files.

Usage:
    python scripts/setup_mock_data.py [--skip-services=SERVICES] [--dry-run]
"""

import argparse
import asyncio
import json
import os
import sys
import subprocess
from pathlib import Path
from typing import Any

import httpx


SCRIPT_DIR = Path(__file__).parent
MOCK_DATA_DIR = SCRIPT_DIR / "mock_data"

AUTH_SERVICE_URL = os.getenv("AUTH_SERVICE_URL", "http://localhost:8001")
CHECKLISTS_SERVICE_URL = os.getenv("CHECKLISTS_SERVICE_URL", "http://localhost:8002")
KNOWLEDGE_SERVICE_URL = os.getenv("KNOWLEDGE_SERVICE_URL", "http://localhost:8003")
NOTIFICATION_SERVICE_URL = os.getenv("NOTIFICATION_SERVICE_URL", "http://localhost:8004")
ESCALATION_SERVICE_URL = os.getenv("ESCALATION_SERVICE_URL", "http://localhost:8005")
MEETING_SERVICE_URL = os.getenv("MEETING_SERVICE_URL", "http://localhost:8006")
FEEDBACK_SERVICE_URL = os.getenv("FEEDBACK_SERVICE_URL", "http://localhost:8007")


POSTGRES_USER = os.getenv("POSTGRES_USER", "roman")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "test_password")
POSTGRES_DB = os.getenv("POSTGRES_DB", "mentor_bot")

ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "admin@company.com")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin123")
API_KEY = os.getenv("API_KEY", "test_api_key")


class Colors:
    RED = "\033[0;31m"
    GREEN = "\033[0;32m"
    YELLOW = "\033[1;33m"
    BLUE = "\033[0;34m"
    CYAN = "\033[0;36m"
    MAGENTA = "\033[0;35m"
    NC = "\033[0m"
    BOLD = "\033[1m"


def log_info(msg: str) -> None:
    print(f"{Colors.CYAN}[INFO]{Colors.NC} {msg}")


def log_success(msg: str) -> None:
    print(f"{Colors.GREEN}[SUCCESS]{Colors.NC} {msg}")


def log_warning(msg: str) -> None:
    print(f"{Colors.YELLOW}[WARNING]{Colors.NC} {msg}")


def log_error(msg: str) -> None:
    print(f"{Colors.RED}[ERROR]{Colors.NC} {msg}")


def log_step(msg: str) -> None:
    print(f"{Colors.BLUE}>>>{Colors.NC} {Colors.BOLD}{msg}{Colors.NC}")


def log_divider() -> None:
    print(f"{Colors.BLUE}{'=' * 50}{Colors.NC}")


def load_json(filename: str) -> Any:
    filepath = MOCK_DATA_DIR / filename
    with open(filepath, "r") as f:
        return json.load(f)


def create_admin_user() -> bool:
    """Create admin user via raw SQL if it doesn't exist."""
    log_step("Creating admin user via database")

    try:
        result = subprocess.run(
            [
                "docker",
                "compose",
                "exec",
                "-T",
                "postgres",
                "psql",
                "-U",
                POSTGRES_USER,
                "-d",
                POSTGRES_DB,
                "-t",
                "-A",
                "-c",
                f"SELECT EXISTS(SELECT 1 FROM auth.users WHERE email = '{ADMIN_EMAIL}');",
            ],
            capture_output=True,
            text=True,
            timeout=10,
        )

        if result.returncode == 0 and "t" in result.stdout.strip():
            log_success(f"Admin user already exists: {ADMIN_EMAIL}")
            return True

        result = subprocess.run(
            [
                "docker",
                "compose",
                "exec",
                "-T",
                "postgres",
                "psql",
                "-U",
                POSTGRES_USER,
                "-d",
                POSTGRES_DB,
                "-c",
                f"""
                INSERT INTO auth.users (
                    email, first_name, last_name, employee_id, password_hash,
                    role, is_active, is_verified, created_at
                ) VALUES (
                    '{ADMIN_EMAIL}', 'Admin', 'Adminov', 'admin001',
                    '$2b$12$qVTIoIpP3.Vee5or6bynf.ZM9Md46J6noG6PNgpFsFJA.w.3XNYN.',
                    'ADMIN', true, true, NOW()
                );
                """,
            ],
            capture_output=True,
            text=True,
            timeout=10,
        )

        if result.returncode == 0:
            log_success(f"Admin user created: {ADMIN_EMAIL}")
            return True
        else:
            log_warning(f"Failed to create admin: {result.stderr}")
            return False

    except FileNotFoundError:
        log_warning("docker compose not found, trying direct psql")
        return create_admin_user_direct()
    except Exception as e:
        log_warning(f"Error creating admin user: {e}")
        return False


def create_admin_user_direct() -> bool:
    """Create admin user using direct psql connection."""
    log_step("Creating admin user via direct database connection")
    try:
        result = subprocess.run(
            [
                "psql",
                f"-U{POSTGRES_USER}",
                "-d",
                POSTGRES_DB,
                "-h",
                "localhost",
                "-p",
                "5432",
                "-c",
                f"""
                INSERT INTO auth.users (
                    email, first_name, last_name, employee_id, password_hash,
                    role, is_active, is_verified, created_at
                ) VALUES (
                    '{ADMIN_EMAIL}', 'Admin', 'Adminov', 'admin001',
                    '$2b$12$qVTIoIpP3.Vee5or6bynf.ZM9Md46J6noG6PNgpFsFJA.w.3XNYN.',
                    'ADMIN', true, true, NOW()
                ) ON CONFLICT (email) DO NOTHING;
                """,
            ],
            capture_output=True,
            text=True,
            timeout=10,
            env={**os.environ, "PGPASSWORD": POSTGRES_PASSWORD},
        )
        if result.returncode == 0:
            log_success(f"Admin user created: {ADMIN_EMAIL}")
            return True
        log_warning(f"Failed to create admin: {result.stderr}")
        return False
    except Exception as e:
        log_warning(f"Error creating admin user: {e}")
        return False


async def wait_for_service(url: str, name: str, max_attempts: int = 30, delay: int = 1) -> bool:
    """Wait for a service to become available."""
    log_step(f"Waiting for {name} to be available")
    async with httpx.AsyncClient(timeout=5.0) as client:
        for attempt in range(1, max_attempts + 1):
            try:
                response = await client.get(f"{url}/health")
                if response.status_code == 200:
                    log_success(f"{name} is available")
                    return True
            except Exception:
                pass
            log_warning(f"Attempt {attempt}/{max_attempts}: {name} not ready yet")
            await asyncio.sleep(delay)
    log_error(f"{name} failed to start after {max_attempts} attempts")
    return False


async def get_admin_token() -> str | None:
    """Get admin authentication token."""
    log_step("Getting admin authentication token")
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"{AUTH_SERVICE_URL}/api/v1/auth/login",
                data={
                    "username": ADMIN_EMAIL,
                    "password": ADMIN_PASSWORD,
                    "grant_type": "password",
                },
                headers={"Content-Type": "application/x-www-form-urlencoded"},
            )
            if response.status_code == 200:
                data = response.json()
                token = data.get("access_token")
                if token:
                    log_success("Admin token obtained")
                    return token
            log_error(f"Failed to get admin token: {response.status_code} - {response.text}")
        except Exception as e:
            log_error(f"Failed to connect to auth service: {e}")
    return None


def create_departments_in_schema(schema: str) -> dict[str, int]:
    """Create departments in a specific service schema via raw SQL."""
    log_step(f"Creating departments in {schema}.departments")
    departments = load_json("departments.json")
    dept_ids: dict[str, int] = {}

    for i, dept in enumerate(departments, start=1):
        name = dept["name"]
        desc = dept.get("description", "").replace("'", "''")

        try:
            result = subprocess.run(
                [
                    "docker",
                    "compose",
                    "exec",
                    "-T",
                    "postgres",
                    "psql",
                    "-U",
                    POSTGRES_USER,
                    "-d",
                    POSTGRES_DB,
                    "-t",
                    "-A",
                    "-c",
                    f"SELECT id FROM {schema}.departments WHERE name = '{name}' LIMIT 1;",
                ],
                capture_output=True,
                text=True,
                timeout=10,
            )

            if result.returncode == 0 and result.stdout.strip():
                dept_id = int(result.stdout.strip())
                dept_ids[name] = dept_id
                log_success(f"  Department '{name}' already exists in {schema} (ID: {dept_id})")
                continue

            result = subprocess.run(
                [
                    "docker",
                    "compose",
                    "exec",
                    "-T",
                    "postgres",
                    "psql",
                    "-U",
                    POSTGRES_USER,
                    "-d",
                    POSTGRES_DB,
                    "-c",
                    f"INSERT INTO {schema}.departments (id, name, description, created_at) VALUES ({i}, '{name}', '{desc}', NOW()) ON CONFLICT DO NOTHING;",
                ],
                capture_output=True,
                text=True,
                timeout=10,
            )

            if result.returncode == 0:
                dept_ids[name] = i
                log_success(f"  Department '{name}' created in {schema} (ID: {i})")
            else:
                log_warning(f"  Failed to create department '{name}' in {schema}: {result.stderr}")

        except Exception as e:
            log_warning(f"  Error creating department '{name}' in {schema}: {e}")

    return dept_ids


async def create_departments(token: str) -> dict[str, int]:
    """Create departments in auth service and all other service schemas."""
    log_step("Creating departments")

    dept_ids = create_departments_in_schema("auth")

    for schema in ["checklists", "knowledge", "meeting"]:
        create_departments_in_schema(schema)

    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    async with httpx.AsyncClient() as client:
        for dept in load_json("departments.json"):
            name = dept["name"]
            try:
                response = await client.get(
                    f"{AUTH_SERVICE_URL}/api/v1/departments/?search={name}",
                    headers=headers,
                )
                if response.status_code == 200:
                    data = response.json()
                    existing = data.get("departments", [])
                    if existing:
                        dept_id = existing[0]["id"]
                        if name not in dept_ids:
                            dept_ids[name] = dept_id
                        log_success(f"  Department '{name}' verified in auth (ID: {dept_id})")
                        continue

                response = await client.post(
                    f"{AUTH_SERVICE_URL}/api/v1/departments/",
                    headers=headers,
                    json=dept,
                )
                if response.status_code in (200, 201):
                    data = response.json()
                    dept_id = data["id"]
                    if name not in dept_ids:
                        dept_ids[name] = dept_id
                    log_success(f"  Department '{name}' created in auth (ID: {dept_id})")
                else:
                    log_warning(f"  Failed to create department '{name}': {response.status_code}")
            except Exception as e:
                log_warning(f"  Error creating department '{name}': {e}")

    return dept_ids


async def create_user(
    client: httpx.AsyncClient,
    token: str,
    user_data: dict,
    dept_ids: dict[str, int],
) -> int | None:
    """Create a user in auth service. Returns user_id or None."""
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    user_payload = {
        "email": user_data["email"],
        "first_name": user_data["first_name"],
        "last_name": user_data["last_name"],
        "employee_id": user_data["employee_id"],
        "password": user_data["password"],
        "role": user_data["role"],
        "position": user_data.get("position"),
        "level": user_data.get("level"),
    }

    dept_name = user_data.get("department")
    if dept_name and dept_name in dept_ids:
        user_payload["department_id"] = dept_ids[dept_name]

    try:
        response = await client.get(
            f"{AUTH_SERVICE_URL}/api/v1/users/by-email/{user_data['email']}",
            headers=headers,
        )
        if response.status_code == 200:
            user_id = response.json()["id"]
            log_success(f"  User '{user_data['email']}' already exists (ID: {user_id})")
            return user_id

        response = await client.post(
            f"{AUTH_SERVICE_URL}/api/v1/users/",
            headers=headers,
            json=user_payload,
        )
        if response.status_code in (200, 201):
            user_id = response.json()["id"]
            log_success(f"  User '{user_data['email']}' created (ID: {user_id})")
            return user_id
        else:
            log_warning(f"  Failed to create user '{user_data['email']}': {response.status_code} - {response.text}")
    except Exception as e:
        log_warning(f"  Error creating user '{user_data['email']}': {e}")
    return None


async def create_invitation_and_register_user(
    token: str,
    user_data: dict,
    dept_ids: dict[str, int],
    mentor_id: int | None = None,
) -> int | None:
    """Create invitation and register user via Telegram."""
    log_step(f"Creating invitation and registering user {user_data['email']}")
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                f"{AUTH_SERVICE_URL}/api/v1/users/by-email/{user_data['email']}",
                headers=headers,
            )
            if response.status_code == 200:
                user_id = response.json()["id"]
                log_success(f"  User already exists: {user_data['email']} (ID: {user_id})")
                return user_id

            inv_payload = {
                "email": user_data["email"],
                "employee_id": user_data["employee_id"],
                "first_name": user_data["first_name"],
                "last_name": user_data["last_name"],
                "role": user_data.get("role", "NEWBIE"),
                "expires_in_days": 7,
            }

            dept_name = user_data.get("department")
            if dept_name and dept_name in dept_ids:
                inv_payload["department_id"] = dept_ids[dept_name]

            if mentor_id:
                inv_payload["mentor_id"] = mentor_id

            if user_data.get("position"):
                inv_payload["position"] = user_data["position"]
            if user_data.get("level"):
                inv_payload["level"] = user_data["level"]

            response = await client.post(
                f"{AUTH_SERVICE_URL}/api/v1/invitations/",
                headers=headers,
                json=inv_payload,
            )
            if response.status_code not in (200, 201):
                log_warning(f"  Failed to create invitation: {response.status_code} - {response.text}")
                return None

            inv_data = response.json()
            inv_token = inv_data.get("token")
            if not inv_token:
                log_warning("  No invitation token in response")
                return None

            log_success(f"  Invitation created: {inv_token[:20]}...")

            reg_payload = {
                "telegram_id": user_data.get("telegram_id", 123456789),
                "username": user_data.get("telegram_username"),
                "first_name": user_data["first_name"],
                "last_name": user_data.get("last_name"),
            }

            response = await client.post(
                f"{AUTH_SERVICE_URL}/api/v1/auth/register/{inv_token}",
                headers={"Content-Type": "application/json", "X-API-Key": API_KEY},
                json=reg_payload,
            )
            if response.status_code in (200, 201):
                response = await client.get(
                    f"{AUTH_SERVICE_URL}/api/v1/users/by-email/{user_data['email']}",
                    headers=headers,
                )
                if response.status_code == 200:
                    user_id = response.json()["id"]
                    log_success(f"  User registered: {user_data['email']} (ID: {user_id})")
                    return user_id

            log_warning(f"  Failed to register user: {response.status_code} - {response.text}")
            return None

        except Exception as e:
            log_warning(f"  Error registering user: {e}")
    return None


async def create_checklist_templates(
    token: str,
    dept_ids: dict[str, int],
    template_data: list[dict],
) -> list[int]:
    """Create checklist templates with tasks."""
    log_step("Creating checklist templates with tasks")
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    template_ids: list[int] = []

    async with httpx.AsyncClient() as client:
        for template in template_data:
            tpl_name = template["name"]
            dept_name = template.get("department")

            dept_id = None
            if dept_name and dept_name in dept_ids:
                dept_id = dept_ids[dept_name]

            tpl_payload = {
                "name": tpl_name,
                "description": template.get("description"),
                "department_id": dept_id,
                "position": template.get("position"),
                "level": template.get("level"),
                "duration_days": template.get("duration_days", 30),
                "task_categories": template.get("task_categories", []),
                "default_assignee_role": template.get("default_assignee_role", "MENTOR"),
                "status": "ACTIVE",
            }

            try:
                response = await client.post(
                    f"{CHECKLISTS_SERVICE_URL}/api/v1/templates/",
                    headers=headers,
                    json=tpl_payload,
                )
                if response.status_code in (200, 201):
                    tpl_data = response.json()
                    tpl_id = tpl_data["id"]
                    template_ids.append(tpl_id)
                    log_success(f"  Template '{tpl_name}' created (ID: {tpl_id})")

                    for task in template.get("tasks", []):
                        task_payload = {
                            "template_id": tpl_id,
                            "title": task["title"],
                            "description": task.get("description"),
                            "instructions": task.get("instructions", ""),
                            "category": task.get("category", "DOCUMENTATION"),
                            "order": task.get("order", 1),
                            "due_days": task.get("due_days", 7),
                            "estimated_minutes": task.get("estimated_minutes", 30),
                            "resources": task.get("resources", []),
                            "required_documents": task.get("required_documents", []),
                            "assignee_role": task.get("assignee_role", "MENTOR"),
                            "auto_assign": task.get("auto_assign", True),
                            "depends_on": task.get("depends_on", []),
                        }
                        await client.post(
                            f"{CHECKLISTS_SERVICE_URL}/api/v1/templates/{tpl_id}/tasks",
                            headers=headers,
                            json=task_payload,
                        )
                    log_success(f"    Added {len(template.get('tasks', []))} tasks to '{tpl_name}'")
                else:
                    log_warning(f"  Failed to create template '{tpl_name}': {response.status_code}")
            except Exception as e:
                log_warning(f"  Error creating template '{tpl_name}': {e}")

    return template_ids


async def create_knowledge_categories(
    token: str,
    dept_ids: dict[str, int],
    category_data: list[dict],
) -> dict[str, int]:
    """Create knowledge base categories."""
    log_step("Creating knowledge base categories")
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    cat_ids: dict[str, int] = {}

    async with httpx.AsyncClient() as client:
        for cat in category_data:
            slug = cat["slug"]
            dept_name = cat.get("department")

            cat_payload = {
                "name": cat["name"],
                "slug": cat["slug"],
                "description": cat.get("description"),
                "position": cat.get("position"),
                "level": cat.get("level"),
                "order": cat.get("order", 0),
                "icon": cat.get("icon"),
                "color": cat.get("color"),
            }

            if dept_name and dept_name in dept_ids:
                cat_payload["department_id"] = dept_ids[dept_name]

            try:
                response = await client.post(
                    f"{KNOWLEDGE_SERVICE_URL}/api/v1/categories/",
                    headers=headers,
                    json=cat_payload,
                )
                if response.status_code in (200, 201):
                    cat_data = response.json()
                    cat_id = cat_data["id"]
                    cat_ids[slug] = cat_id
                    log_success(f"  Category '{cat['name']}' created (ID: {cat_id})")
                else:
                    log_warning(f"  Failed to create category '{cat['name']}': {response.status_code}")
            except Exception as e:
                log_warning(f"  Error creating category '{cat['name']}': {e}")

    return cat_ids


async def create_knowledge_tags(
    token: str,
    tag_data: list[dict],
) -> dict[str, int]:
    """Create knowledge base tags."""
    log_step("Creating knowledge base tags")
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    tag_ids: dict[str, int] = {}

    async with httpx.AsyncClient() as client:
        for tag in tag_data:
            slug = tag["slug"]
            try:
                response = await client.post(
                    f"{KNOWLEDGE_SERVICE_URL}/api/v1/tags/",
                    headers=headers,
                    json=tag,
                )
                if response.status_code in (200, 201):
                    tag_data_resp = response.json()
                    tag_id = tag_data_resp["id"]
                    tag_ids[slug] = tag_id
                    log_success(f"  Tag '{tag['name']}' created (ID: {tag_id})")
                else:
                    log_warning(f"  Failed to create tag '{tag['name']}': {response.status_code}")
            except Exception as e:
                log_warning(f"  Error creating tag '{tag['name']}': {e}")

    return tag_ids


async def create_knowledge_articles(
    token: str,
    cat_ids: dict[str, int],
    tag_ids: dict[str, int],
    dept_ids: dict[str, int],
    article_data: list[dict],
) -> list[int]:
    """Create knowledge base articles."""
    log_step("Creating knowledge base articles")
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    article_ids: list[int] = []

    async with httpx.AsyncClient() as client:
        for article in article_data:
            cat_slug = article.get("category")
            cat_id = cat_ids.get(cat_slug) if cat_slug else None

            tag_list = article.get("tags", [])
            tag_id_list = [tag_ids.get(slug) for slug in tag_list if tag_ids.get(slug)]

            dept_name = article.get("department")
            dept_id = dept_ids.get(dept_name) if dept_name else None

            art_payload = {
                "title": article["title"],
                "content": article["content"],
                "excerpt": article.get("excerpt"),
                "category_id": cat_id,
                "department_id": dept_id,
                "position": article.get("position"),
                "level": article.get("level"),
                "status": article.get("status", "PUBLISHED"),
                "is_pinned": article.get("is_pinned", False),
                "keywords": article.get("keywords", []),
                "tag_ids": tag_id_list,
            }

            try:
                response = await client.post(
                    f"{KNOWLEDGE_SERVICE_URL}/api/v1/articles/",
                    headers=headers,
                    json=art_payload,
                )
                if response.status_code in (200, 201):
                    art_data = response.json()
                    art_id = art_data["id"]
                    article_ids.append(art_id)
                    log_success(
                        f"  Article '{article['title']}' created (ID: {art_id}, status: {article.get('status')})"
                    )
                else:
                    log_warning(f"  Failed to create article '{article['title']}': {response.status_code}")
            except Exception as e:
                log_warning(f"  Error creating article '{article['title']}': {e}")

    return article_ids


async def create_dialogue_scenarios(
    token: str,
    scenario_data: list[dict],
) -> None:
    """Create dialogue scenarios with steps."""
    log_step("Creating dialogue scenarios with steps")
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    async with httpx.AsyncClient() as client:
        for scenario in scenario_data:
            scenario_title = scenario["title"]
            try:
                response = await client.post(
                    f"{KNOWLEDGE_SERVICE_URL}/api/v1/dialogue-scenarios/",
                    headers=headers,
                    json=scenario,
                )
                if response.status_code in (200, 201):
                    log_success(f"  Scenario '{scenario_title}' created")
                else:
                    log_warning(
                        f"  Failed to create scenario '{scenario_title}': {response.status_code} - {response.text}"
                    )
            except Exception as e:
                log_warning(f"  Error creating scenario '{scenario_title}': {e}")


async def create_meetings(
    token: str,
    dept_ids: dict[str, int],
    meeting_data: list[dict],
) -> list[int]:
    """Create meeting templates."""
    log_step("Creating meeting templates")
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    meeting_ids: list[int] = []

    async with httpx.AsyncClient() as client:
        for meeting in meeting_data:
            dept_name = meeting.get("department")

            meet_payload = {
                "title": meeting["title"],
                "description": meeting.get("description"),
                "type": meeting.get("type", "OTHER"),
                "position": meeting.get("position"),
                "level": meeting.get("level"),
                "is_mandatory": meeting.get("is_mandatory", True),
                "deadline_days": meeting.get("deadline_days", 7),
                "order": meeting.get("order", 0),
            }

            if dept_name and dept_name in dept_ids:
                meet_payload["department_id"] = dept_ids[dept_name]

            try:
                response = await client.post(
                    f"{MEETING_SERVICE_URL}/api/v1/meetings/",
                    headers=headers,
                    json=meet_payload,
                )
                if response.status_code in (200, 201):
                    meet_data = response.json()
                    meet_id = meet_data["id"]
                    meeting_ids.append(meet_id)
                    log_success(f"  Meeting '{meeting['title']}' created (ID: {meet_id})")
                else:
                    log_warning(f"  Failed to create meeting '{meeting['title']}': {response.status_code}")
            except Exception as e:
                log_warning(f"  Error creating meeting '{meeting['title']}': {e}")

    return meeting_ids


async def create_notifications(
    user_ids: list[int],
    notification_data: list[dict],
) -> None:
    """Create sample notifications."""
    if not user_ids:
        log_warning("No user IDs available for notifications")
        return

    log_step("Creating sample notifications")
    headers = {"Content-Type": "application/json"}

    async with httpx.AsyncClient() as client:
        for notif in notification_data:
            for user_id in user_ids[:3]:
                notif_payload = {
                    "user_id": user_id,
                    "type": notif.get("type", "GENERAL"),
                    "channel": notif.get("channel", "TELEGRAM"),
                    "subject": notif.get("subject"),
                    "body": notif.get("body", "Sample notification"),
                    "data": notif.get("sample_data", {}),
                }
                try:
                    response = await client.post(
                        f"{NOTIFICATION_SERVICE_URL}/api/v1/notifications/send",
                        headers=headers,
                        json=notif_payload,
                    )
                    if response.status_code in (200, 201):
                        log_success(f"  Notification sent to user {user_id}")
                except Exception as e:
                    log_warning(f"  Error sending notification: {e}")


async def create_escalations(
    user_ids: list[int],
    escalation_data: list[dict],
) -> None:
    """Create sample escalations."""
    if not user_ids:
        log_warning("No user IDs available for escalations")
        return

    log_step("Creating sample escalations")
    headers = {"Content-Type": "application/json"}

    async with httpx.AsyncClient() as client:
        for esc in escalation_data[:3]:
            if not user_ids:
                break

            esc_payload = {
                "user_id": user_ids[0],
                "type": esc.get("type", "GENERAL"),
                "source": esc.get("source", "MANUAL"),
                "reason": esc.get("reason"),
                "context": esc.get("context", {}),
                "related_entity_type": esc.get("related_entity_type"),
                "related_entity_id": esc.get("related_entity_id"),
            }
            try:
                response = await client.post(
                    f"{ESCALATION_SERVICE_URL}/api/v1/escalations/",
                    headers=headers,
                    json=esc_payload,
                )
                if response.status_code in (200, 201):
                    log_success(f"  Escalation created for user {user_ids[0]}")
            except Exception as e:
                log_warning(f"  Error creating escalation: {e}")


async def create_feedback(
    user_ids: list[int],
    feedback_data: dict,
) -> None:
    """Create sample feedback."""
    if not user_ids:
        log_warning("No user IDs available for feedback")
        return

    log_step("Creating sample feedback")

    async with httpx.AsyncClient() as client:
        pulse_data = feedback_data.get("pulse_surveys", [])
        for i, pulse in enumerate(pulse_data[:3]):
            if i >= len(user_ids):
                break
            payload = {"user_id": user_ids[i], "rating": pulse.get("rating", 7)}
            try:
                response = await client.post(
                    f"{FEEDBACK_SERVICE_URL}/api/v1/feedback/pulse",
                    json=payload,
                )
                if response.status_code in (200, 201):
                    log_success(f"  Pulse survey created for user {user_ids[i]}")
            except Exception as e:
                log_warning(f"  Error creating pulse survey: {e}")

        exp_data = feedback_data.get("experience_ratings", [])
        for i, exp in enumerate(exp_data[:3]):
            if i >= len(user_ids):
                break
            payload = {"user_id": user_ids[i], "rating": exp.get("rating", 4)}
            try:
                response = await client.post(
                    f"{FEEDBACK_SERVICE_URL}/api/v1/feedback/experience",
                    json=payload,
                )
                if response.status_code in (200, 201):
                    log_success(f"  Experience rating created for user {user_ids[i]}")
            except Exception as e:
                log_warning(f"  Error creating experience rating: {e}")

        comment_data = feedback_data.get("comments", [])
        for i, comment in enumerate(comment_data[:3]):
            if i >= len(user_ids):
                break
            payload = {"user_id": user_ids[i], "comment": comment.get("comment", "Great experience!")}
            try:
                response = await client.post(
                    f"{FEEDBACK_SERVICE_URL}/api/v1/feedback/comments",
                    json=payload,
                )
                if response.status_code in (200, 201):
                    log_success(f"  Comment created for user {user_ids[i]}")
            except Exception as e:
                log_warning(f"  Error creating comment: {e}")


async def create_pending_invitations(
    token: str,
    dept_ids: dict[str, int],
    mentor_id: int | None = None,
) -> None:
    """Create pending invitations that are not registered yet."""
    log_step("Creating pending invitations")
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    pending_invitations = [
        {
            "email": "pending@company.com",
            "employee_id": "EMP999",
            "first_name": "Pending",
            "last_name": "User",
            "role": "NEWBIE",
            "department": "Engineering",
            "position": "Software Engineer",
            "level": "JUNIOR",
        },
    ]

    async with httpx.AsyncClient() as client:
        for inv in pending_invitations:
            inv_payload = {
                "email": inv["email"],
                "employee_id": inv["employee_id"],
                "first_name": inv["first_name"],
                "last_name": inv["last_name"],
                "role": inv.get("role", "NEWBIE"),
                "expires_in_days": 7,
            }

            dept_name = inv.get("department")
            if dept_name and dept_name in dept_ids:
                inv_payload["department_id"] = dept_ids[dept_name]

            if inv.get("position"):
                inv_payload["position"] = inv["position"]
            if inv.get("level"):
                inv_payload["level"] = inv["level"]
            if mentor_id:
                inv_payload["mentor_id"] = mentor_id

            try:
                response = await client.post(
                    f"{AUTH_SERVICE_URL}/api/v1/invitations/",
                    headers=headers,
                    json=inv_payload,
                )
                if response.status_code in (200, 201):
                    inv_data = response.json()
                    log_success(
                        f"  Pending invitation created: {inv['email']} (token: {inv_data.get('token', 'N/A')[:20]}...)"
                    )
                else:
                    log_warning(f"  Failed to create pending invitation: {response.status_code}")
            except Exception as e:
                log_warning(f"  Error creating pending invitation: {e}")


async def main(skip_services: list[str] | None = None, dry_run: bool = False) -> None:
    skip_services = skip_services or []

    log_divider()
    log_step("Mock Data Setup for Mentor Bot")
    log_divider()

    if dry_run:
        log_warning("Running in DRY-RUN mode - no data will be created")

    log_step("Checking services availability")

    services = [
        (AUTH_SERVICE_URL, "Auth Service"),
        (CHECKLISTS_SERVICE_URL, "Checklists Service"),
        (KNOWLEDGE_SERVICE_URL, "Knowledge Service"),
    ]

    if "notification" not in skip_services:
        services.append((NOTIFICATION_SERVICE_URL, "Notification Service"))
    if "escalation" not in skip_services:
        services.append((ESCALATION_SERVICE_URL, "Escalation Service"))
    if "meeting" not in skip_services:
        services.append((MEETING_SERVICE_URL, "Meeting Service"))
    if "feedback" not in skip_services:
        services.append((FEEDBACK_SERVICE_URL, "Feedback Service"))

    for url, name in services:
        if not await wait_for_service(url, name):
            log_error(f"{name} is not available. Exiting.")
            sys.exit(1)

    if not dry_run:
        if not create_admin_user():
            log_error("Failed to create admin user. Exiting.")
            sys.exit(1)

    token = await get_admin_token()
    if not token:
        log_error("Failed to get admin token. Exiting.")
        sys.exit(1)

    log_divider()
    log_step("Creating mock data")
    log_divider()

    users_data = load_json("users.json")
    dept_ids = await create_departments(token)

    user_ids: list[int] = []
    admin_id: int | None = None

    admin_id = await create_user(httpx.AsyncClient(), token, users_data["admin"], dept_ids)
    if admin_id:
        user_ids.append(admin_id)

    hr_id = await create_user(httpx.AsyncClient(), token, users_data["hr"], dept_ids)
    if hr_id:
        user_ids.append(hr_id)

    mentor_id = await create_user(httpx.AsyncClient(), token, users_data["mentor"], dept_ids)
    if mentor_id:
        user_ids.append(mentor_id)

    if "checklists" not in skip_services:
        templates = load_json("templates.json")
        await create_checklist_templates(token, dept_ids, templates)

    newbie_id = await create_invitation_and_register_user(token, users_data["newbie"], dept_ids, mentor_id)
    if newbie_id:
        user_ids.append(newbie_id)

    await create_pending_invitations(token, dept_ids, mentor_id)

    extra_hr_id = await create_user(httpx.AsyncClient(), token, users_data.get("extra_hr", {}), dept_ids)
    if extra_hr_id:
        user_ids.append(extra_hr_id)

    extra_mentor_id = await create_user(httpx.AsyncClient(), token, users_data.get("extra_mentor", {}), dept_ids)
    if extra_mentor_id:
        user_ids.append(extra_mentor_id)

    if "knowledge" not in skip_services:
        categories = load_json("knowledge_categories.json")
        cat_ids = await create_knowledge_categories(token, dept_ids, categories)

        tags = load_json("knowledge_tags.json")
        tag_ids = await create_knowledge_tags(token, tags)

        articles = load_json("knowledge_articles.json")
        await create_knowledge_articles(token, cat_ids, tag_ids, dept_ids, articles)

    if "meeting" not in skip_services:
        meetings = load_json("meetings.json")
        await create_meetings(token, dept_ids, meetings)

    if "notification" not in skip_services:
        notifications = load_json("notifications.json")
        await create_notifications(user_ids, notifications)

    if "escalation" not in skip_services:
        escalations = load_json("escalations.json")
        await create_escalations(user_ids, escalations)

    if "feedback" not in skip_services:
        feedback = load_json("feedback.json")
        await create_feedback(user_ids, feedback)

    if "knowledge" not in skip_services:
        scenarios = load_json("dialogue_scenarios.json")
        await create_dialogue_scenarios(token, scenarios)

    log_divider()
    log_success("Mock data setup completed successfully!")
    log_divider()
    log_info("Summary:")
    log_info(f"  Departments:      {len(dept_ids)}")
    log_info(f"  Users:            {len(user_ids)}")
    if "checklists" not in skip_services:
        log_info(f"  Templates:        {len(load_json('templates.json'))}")
    if "knowledge" not in skip_services:
        log_info(f"  Categories:       {len(load_json('knowledge_categories.json'))}")
        log_info(f"  Tags:             {len(load_json('knowledge_tags.json'))}")
        log_info(f"  Articles:         {len(load_json('knowledge_articles.json'))}")
        log_info(f"  Dialogue scenarios: {len(load_json('dialogue_scenarios.json'))}")
    if "meeting" not in skip_services:
        log_info(f"  Meetings:         {len(load_json('meetings.json'))}")
    if "notification" not in skip_services:
        log_info(f"  Notifications:    {len(load_json('notifications.json'))}")
    if "escalation" not in skip_services:
        log_info(f"  Escalations:      {len(load_json('escalations.json'))}")
    if "feedback" not in skip_services:
        log_info(
            f"  Feedback entries: {len(load_json('feedback.json')['pulse_surveys']) + len(load_json('feedback.json')['experience_ratings']) + len(load_json('feedback.json')['comments'])}"
        )
    log_divider()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Setup mock data for Mentor Bot")
    parser.add_argument(
        "--skip-services",
        type=str,
        default="",
        help="Comma-separated list of services to skip (e.g., 'notification,escalation')",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Run without actually creating data",
    )

    args = parser.parse_args()
    skip_list = [s.strip() for s in args.skip_services.split(",") if s.strip()]

    asyncio.run(main(skip_services=skip_list, dry_run=args.dry_run))
