#!/usr/bin/env python3
"""
Mock Data Setup Script for Mentor Bot.

Creates test data across all microservices using JSON configuration files.
Generates rich data for demonstration purposes - various statuses, roles, etc.

All API calls are routed through a single admin_web entry point. The admin_web
Next.js app exposes a catch-all proxy at /api/v1/<service>/... that forwards
to the appropriate backend service inside the Docker network. This lets the
script work in both dev (where ports are exposed) and prod (where only the
admin_web is publicly reachable).

Usage:
    python scripts/setup_mock_data.py [--admin-web-url=URL] [--skip-services=SERVICES] [--dry-run]
"""

import argparse
import asyncio
import json
import os
import subprocess
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

import httpx

SCRIPT_DIR = Path(__file__).parent
MOCK_DATA_DIR = SCRIPT_DIR / "mock_data"


# This script is host-side: service URLs in .env (e.g. http://auth_service:8000)
# only resolve inside the docker network, so we ignore them here. We pick up
# DB credentials needed to bootstrap the admin user via psql, and ADMIN_WEB_URL
# for routing all API calls through the admin_web proxy.
_ENV_KEYS_TO_LOAD = {
    "POSTGRES_USER",
    "POSTGRES_PASSWORD",
    "AUTH_DB",
    "ADMIN_EMAIL",
    "ADMIN_PASSWORD",
    "SERVICE_API_KEY",
    "ADMIN_WEB_URL",
}


def _load_env_file() -> None:
    """Load selected DB-related values from project-root .env into os.environ."""
    env_path = SCRIPT_DIR.parent / ".env"
    if not env_path.exists():
        return
    for raw in env_path.read_text().splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        if key not in _ENV_KEYS_TO_LOAD:
            continue
        os.environ.setdefault(key, value.strip().strip('"').strip("'"))


_load_env_file()

# Single entry point: admin_web proxies /api/v1/<service>/... to the right backend.
ADMIN_WEB_URL = os.getenv("ADMIN_WEB_URL", "http://localhost:3000").rstrip("/")


POSTGRES_USER = os.getenv("POSTGRES_USER", "postgres")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "changeme")
# Auth lives in its own DB under db-per-service architecture.
AUTH_DB = os.getenv("AUTH_DB", "auth_db")

ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "admin@company.com")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin123")
SERVICE_API_KEY = os.getenv("SERVICE_API_KEY", "test_api_key")


class Colors:
    """Terminal color codes for logging."""

    RED = "\033[0;31m"
    GREEN = "\033[0;32m"
    YELLOW = "\033[1;33m"
    BLUE = "\033[0;34m"
    CYAN = "\033[0;36m"
    MAGENTA = "\033[0;35m"
    NC = "\033[0m"
    BOLD = "\033[1m"


def log_info(msg: str) -> None:
    """Print info message to console."""
    print(f"{Colors.CYAN}[INFO]{Colors.NC} {msg}")


def log_success(msg: str) -> None:
    """Print success message to console."""
    print(f"{Colors.GREEN}[SUCCESS]{Colors.NC} {msg}")


def log_warning(msg: str) -> None:
    """Print warning message to console."""
    print(f"{Colors.YELLOW}[WARNING]{Colors.NC} {msg}")


def log_error(msg: str) -> None:
    """Print error message to console."""
    print(f"{Colors.RED}[ERROR]{Colors.NC} {msg}")


def log_step(msg: str) -> None:
    """Print step message to console."""
    print(f"{Colors.BLUE}>>>{Colors.NC} {Colors.BOLD}{msg}{Colors.NC}")


def log_divider() -> None:
    """Print divider line to console."""
    print(f"{Colors.BLUE}{'=' * 60}{Colors.NC}")


def load_json(filename: str) -> Any:
    """Load JSON file from mock data directory."""
    filepath = MOCK_DATA_DIR / filename
    with open(filepath) as f:
        return json.load(f)


_INSERT_ADMIN_SQL = """
INSERT INTO users (
    email, first_name, last_name, employee_id, password_hash,
    role, is_active, is_verified, created_at
) VALUES (
    '{email}', 'Admin', 'Adminov', 'admin001',
    '$2b$12$qVTIoIpP3.Vee5or6bynf.ZM9Md46J6noG6PNgpFsFJA.w.3XNYN.',
    'ADMIN', true, true, NOW()
) ON CONFLICT (email) DO NOTHING;
"""


def create_admin_user() -> bool:
    """Create admin user via raw SQL if it doesn't exist."""
    log_step(f"Creating admin user in {AUTH_DB}")

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
                AUTH_DB,
                "-t",
                "-A",
                "-c",
                f"SELECT EXISTS(SELECT 1 FROM users WHERE email = '{ADMIN_EMAIL}');",
            ],
            capture_output=True,
            text=True,
            timeout=10,
        )

        if result.returncode == 0 and result.stdout.strip() == "t":
            log_success(f"Admin user already exists: {ADMIN_EMAIL}")
            return True

        if result.returncode != 0:
            log_warning(f"Existence check via docker failed: {result.stderr.strip()}")
            return create_admin_user_direct()

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
                AUTH_DB,
                "-c",
                _INSERT_ADMIN_SQL.format(email=ADMIN_EMAIL),
            ],
            capture_output=True,
            text=True,
            timeout=10,
        )

        if result.returncode == 0:
            log_success(f"Admin user created: {ADMIN_EMAIL}")
            return True
        log_warning(f"Failed to create admin: {result.stderr.strip()}")
        return False

    except FileNotFoundError:
        log_warning("docker compose not found, trying direct psql")
        return create_admin_user_direct()
    except Exception as e:
        log_warning(f"Error creating admin user: {e}")
        return False


def create_admin_user_direct() -> bool:
    """Create admin user using direct psql connection (fallback)."""
    log_step("Creating admin user via direct psql on localhost:5432")
    try:
        result = subprocess.run(
            [
                "psql",
                "-U",
                POSTGRES_USER,
                "-d",
                AUTH_DB,
                "-h",
                "localhost",
                "-p",
                "5432",
                "-c",
                _INSERT_ADMIN_SQL.format(email=ADMIN_EMAIL),
            ],
            capture_output=True,
            text=True,
            timeout=10,
            env={**os.environ, "PGPASSWORD": POSTGRES_PASSWORD},
        )
        if result.returncode == 0:
            log_success(f"Admin user created: {ADMIN_EMAIL}")
            return True
        log_warning(f"Failed to create admin: {result.stderr.strip()}")
        return False
    except Exception as e:
        log_warning(f"Error creating admin user: {e}")
        return False


async def wait_for_admin_web(url: str, max_attempts: int = 30, delay: int = 1) -> bool:
    """Wait for admin_web to become reachable.

    Next.js doesn't ship a /health route by default; any 2xx/3xx from the root
    means the app is up and the API proxy is ready to forward requests.
    """
    log_step(f"Waiting for admin_web at {url}")
    async with httpx.AsyncClient(timeout=5.0, follow_redirects=False) as client:
        for attempt in range(1, max_attempts + 1):
            try:
                response = await client.get(f"{url}/")
                if 200 <= response.status_code < 400:
                    log_success("admin_web is available")
                    return True
            except Exception:
                pass
            log_warning(f"Attempt {attempt}/{max_attempts}: admin_web not ready yet")
            await asyncio.sleep(delay)
    log_error(f"admin_web failed to respond after {max_attempts} attempts")
    return False


async def get_admin_token() -> str | None:
    """Get admin authentication token."""
    log_step("Getting admin authentication token")
    async with httpx.AsyncClient(follow_redirects=True) as client:
        try:
            response = await client.post(
                f"{ADMIN_WEB_URL}/api/v1/auth/login",
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


async def create_departments(token: str) -> dict[str, int]:
    """Create departments via auth service API (which syncs to other services automatically)."""
    log_step("Creating departments")
    departments = load_json("departments.json")
    dept_ids: dict[str, int] = {}
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    async with httpx.AsyncClient(follow_redirects=True) as client:
        tasks = [_create_or_get_department(client, headers, dept) for dept in departments]
        results = await asyncio.gather(*tasks)

    dept_ids = {name: dept_id for name, dept_id in results if dept_id is not None}
    return dept_ids


async def _create_or_get_department(
    client: httpx.AsyncClient,
    headers: dict[str, str],
    dept: dict,
) -> tuple[str, int | None]:
    """Create a department via auth API or return existing ID. Auth service syncs to other services."""
    name = dept["name"]
    try:
        response = await client.get(
            f"{ADMIN_WEB_URL}/api/v1/departments/",
            headers=headers,
            params={"search": name},
        )
        if response.status_code == 200:
            existing = response.json().get("departments", [])
            if existing:
                dept_id = existing[0]["id"]
                log_success(f"  Department '{name}' already exists (ID: {dept_id})")
                return name, dept_id

        response = await client.post(
            f"{ADMIN_WEB_URL}/api/v1/departments/",
            headers=headers,
            json=dept,
        )
        if response.status_code in (200, 201):
            dept_id = response.json()["id"]
            log_success(f"  Department '{name}' created (ID: {dept_id})")
            return name, dept_id
        log_warning(f"  Failed to create department '{name}': {response.status_code} - {response.text}")
    except Exception as e:
        log_warning(f"  Error creating department '{name}': {e}")
    return name, None


async def create_user(
    client: httpx.AsyncClient,
    token: str,
    user_data: dict,
    dept_ids: dict[str, int],
) -> tuple[str, int | None]:
    """Create a user in auth service. Returns (user_key, user_id) or (user_key, None)."""
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
        "telegram_id": user_data.get("telegram_id"),
    }

    dept_name = user_data.get("department")
    if dept_name and dept_name in dept_ids:
        user_payload["department_id"] = dept_ids[dept_name]

    try:
        response = await client.get(
            f"{ADMIN_WEB_URL}/api/v1/users/by-email/{user_data['email']}",
            headers=headers,
        )
        if response.status_code == 200:
            user_id = response.json()["id"]
            log_success(f"  User '{user_data['email']}' already exists (ID: {user_id})")
            return (user_data.get("key", ""), user_id)

        response = await client.post(
            f"{ADMIN_WEB_URL}/api/v1/users/",
            headers=headers,
            json=user_payload,
        )
        if response.status_code in (200, 201):
            user_id = response.json()["id"]
            log_success(f"  User '{user_data['email']}' created (ID: {user_id})")
            return (user_data.get("key", ""), user_id)
        log_warning(f"  Failed to create user '{user_data['email']}': {response.status_code} - {response.text}")
    except Exception as e:
        log_warning(f"  Error creating user '{user_data['email']}': {e}")
    return (user_data.get("key", ""), None)


async def create_all_users_async(
    token: str,
    dept_ids: dict[str, int],
) -> tuple[dict[str, int], list[int], list[int]]:
    """Create all users asynchronously in parallel."""
    log_step("Creating users (async parallel)")

    users_data = load_json("users.json")

    enriched_users = []
    for key, user in users_data.items():
        user_with_key = dict(user)
        user_with_key["key"] = key
        enriched_users.append(user_with_key)

    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
        tasks = [create_user(client, token, user, dept_ids) for user in enriched_users]
        results = await asyncio.gather(*tasks)

    user_ids: dict[str, int] = {}
    mentor_ids: list[int] = []
    hr_ids: list[int] = []

    for key, user_data in zip([u["key"] for u in enriched_users], enriched_users):
        for result_key, user_id in results:
            if result_key == key and user_id:
                user_ids[key] = user_id
                if user_data.get("role") == "MENTOR":
                    mentor_ids.append(user_id)
                elif user_data.get("role") in ["HR", "ADMIN"]:
                    hr_ids.append(user_id)

    log_step(f"Created {len(user_ids)} users: {len(mentor_ids)} mentors, {len(hr_ids)} HR")
    return user_ids, mentor_ids, hr_ids


async def create_checklist_templates(
    token: str,
    dept_ids: dict[str, int],
    template_data: list[dict],
) -> list[int]:
    """Create checklist templates with tasks."""
    log_step("Creating checklist templates with tasks")
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    template_ids: list[int] = []

    async with httpx.AsyncClient(follow_redirects=True) as client:
        async def create_template(template: dict) -> int | None:
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
                    f"{ADMIN_WEB_URL}/api/v1/templates/",
                    headers=headers,
                    json=tpl_payload,
                )
                if response.status_code in (200, 201):
                    tpl_data = response.json()
                    tpl_id = tpl_data["id"]
                    log_success(f"  Template '{tpl_name}' created (ID: {tpl_id})")

                    # Create tasks for this template in parallel
                    tasks = template.get("tasks", [])
                    async def create_task(task: dict) -> None:
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
                            f"{ADMIN_WEB_URL}/api/v1/templates/{tpl_id}/tasks",
                            headers=headers,
                            json=task_payload,
                        )

                    if tasks:
                        await asyncio.gather(*[create_task(task) for task in tasks])
                        log_success(f"    Added {len(tasks)} tasks to '{tpl_name}'")

                    return tpl_id
                log_warning(f"  Failed to create template '{tpl_name}': {response.status_code} - {response.text}")
            except Exception as e:
                log_warning(f"  Error creating template '{tpl_name}': {e}")
            return None

        results = await asyncio.gather(*[create_template(tpl) for tpl in template_data])
        template_ids = [tid for tid in results if tid is not None]

    return template_ids


async def create_checklist_instances_async(
    token: str,
    template_ids: list[int],
    users_data: dict,
    user_ids: dict[str, int],
    mentor_id: int | None,
    hr_id: int | None,
) -> None:
    """Create all checklist instances asynchronously."""
    log_step("Creating checklist instances (async)")

    checklist_instances = load_json("checklist_instances.json")

    async def create_single_instance(instance: dict) -> None:
        newbie_key = instance.get("user_key")
        status = instance.get("status")
        days_ago = instance.get("days_ago", 0)
        completed_tasks = instance.get("completed_tasks", 0)
        template_index = instance.get("template_index", 0)

        if newbie_key in user_ids:
            await create_checklist_instances(
                token,
                template_ids,
                users_data[newbie_key],
                user_ids[newbie_key],
                mentor_id,
                hr_id,
                status,
                days_ago,
                completed_tasks,
                template_index,
            )

    await asyncio.gather(*[create_single_instance(inst) for inst in checklist_instances])


async def create_checklist_instances(
    token: str,
    template_ids: list[int],
    user_data: dict,
    user_id: int,
    mentor_id: int | None,
    hr_id: int | None,
    status: str,
    start_days_ago: int = 0,
    completed_task_count: int = 0,
    template_index: int = 0,
) -> int | None:
    """Create a checklist instance for a user using specified template index."""
    if not template_ids:
        return None

    # Use the specified template index (with wraparound if index is out of range)
    tpl_id = template_ids[template_index % len(template_ids)]

    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    start_date = datetime.now() - timedelta(days=start_days_ago)

    async with httpx.AsyncClient(follow_redirects=True) as client:
        try:
            checklist_data = {
                "user_id": user_id,
                "employee_id": user_data["employee_id"],
                "template_id": tpl_id,
                "start_date": start_date.isoformat(),
                "mentor_id": mentor_id,
                "hr_id": hr_id,
            }

            response = await client.post(
                f"{ADMIN_WEB_URL}/api/v1/checklists/",
                headers=headers,
                json=checklist_data,
            )

            if response.status_code in (200, 201):
                checklist = response.json()
                checklist_id = checklist["id"]
                log_success(f"  Checklist {checklist_id} created for user {user_id} (status: {status}, template: {template_index})")

                if completed_task_count > 0:
                    await update_checklist_tasks(client, headers, checklist_id, completed_task_count, status)

                if status == "COMPLETED":
                    # Use PUT endpoint to update status to COMPLETED
                    # The update_checklist service automatically marks all pending tasks as COMPLETED
                    complete_resp = await client.put(
                        f"{ADMIN_WEB_URL}/api/v1/checklists/{checklist_id}",
                        headers=headers,
                        json={"status": "COMPLETED"},
                    )
                    if complete_resp.status_code in (200, 201):
                        log_success(f"  Checklist {checklist_id} marked as completed")
                    else:
                        log_warning(f"  Failed to complete checklist {checklist_id}: {complete_resp.status_code} - {complete_resp.text}")

                return checklist_id

        except Exception as e:
            log_warning(f"  Error creating checklist: {e}")

    return None


async def update_checklist_tasks(
    client: httpx.AsyncClient,
    headers: dict,
    checklist_id: int,
    completed_count: int,
    status: str,
) -> None:
    """Update tasks within a checklist to show progress."""
    try:
        # Fetch tasks for this checklist
        response = await client.get(
            f"{ADMIN_WEB_URL}/api/v1/tasks/checklist/{checklist_id}",
            headers=headers,
        )

        if response.status_code != 200:
            log_warning(f"  Failed to fetch tasks for checklist {checklist_id}: {response.status_code}")
            return

        tasks = response.json()
        if not isinstance(tasks, list):
            tasks = tasks.get("tasks", [])

        if not tasks:
            log_warning(f"  No tasks found for checklist {checklist_id}")
            return

        # For in-progress, complete specified count of tasks
        if completed_count > 0:
            for i, task in enumerate(tasks):
                if i < completed_count:
                    task_id = task["id"]
                    await client.post(
                        f"{ADMIN_WEB_URL}/api/v1/tasks/{task_id}/complete",
                        headers=headers,
                    )
    except Exception as e:
        log_warning(f"  Error updating tasks for checklist {checklist_id}: {e}")


async def create_knowledge_categories(
    token: str,
    dept_ids: dict[str, int],
    category_data: list[dict],
) -> dict[str, int]:
    """Create knowledge base categories."""
    log_step("Creating knowledge base categories")
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    async with httpx.AsyncClient(follow_redirects=True) as client:
        async def create_category(cat: dict) -> tuple[str, int | None]:
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
                    f"{ADMIN_WEB_URL}/api/v1/categories/",
                    headers=headers,
                    json=cat_payload,
                )
                if response.status_code in (200, 201):
                    cat_data = response.json()
                    cat_id = cat_data["id"]
                    log_success(f"  Category '{cat['name']}' created (ID: {cat_id})")
                    return (slug, cat_id)
                log_warning(f"  Failed to create category '{cat['name']}': {response.status_code} - {response.text}")
            except Exception as e:
                log_warning(f"  Error creating category '{cat['name']}': {e}")
            return (slug, None)

        # Create categories with small delay between each to avoid overwhelming the DB
        cat_ids = {}
        for cat in category_data:
            slug, cat_id = await create_category(cat)
            if cat_id is not None:
                cat_ids[slug] = cat_id
            await asyncio.sleep(0.1)  # Small delay between requests

    return cat_ids


async def create_knowledge_tags(
    token: str,
    tag_data: list[dict],
) -> dict[str, int]:
    """Create knowledge base tags."""
    log_step("Creating knowledge base tags")
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    async with httpx.AsyncClient(follow_redirects=True) as client:
        async def create_tag(tag: dict) -> tuple[str, int | None]:
            slug = tag["slug"]
            try:
                response = await client.post(
                    f"{ADMIN_WEB_URL}/api/v1/tags/",
                    headers=headers,
                    json=tag,
                )
                if response.status_code in (200, 201):
                    tag_data_resp = response.json()
                    tag_id = tag_data_resp["id"]
                    log_success(f"  Tag '{tag['name']}' created (ID: {tag_id})")
                    return (slug, tag_id)
                log_warning(f"  Failed to create tag '{tag['name']}': {response.status_code} - {response.text}")
            except Exception as e:
                log_warning(f"  Error creating tag '{tag['name']}': {e}")
            return (slug, None)

        # Create tags with small delay between each to avoid overwhelming the DB
        tag_ids = {}
        for tag in tag_data:
            slug, tag_id = await create_tag(tag)
            if tag_id is not None:
                tag_ids[slug] = tag_id
            await asyncio.sleep(0.1)  # Small delay between requests

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

    async with httpx.AsyncClient(follow_redirects=True) as client:
        async def create_article(article: dict) -> int | None:
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
                    f"{ADMIN_WEB_URL}/api/v1/articles/",
                    headers=headers,
                    json=art_payload,
                )
                if response.status_code in (200, 201):
                    art_data = response.json()
                    art_id = art_data["id"]
                    log_success(
                        f"  Article '{article['title']}' created (ID: {art_id}, status: {article.get('status')})"
                    )
                    return art_id
                log_warning(f"  Failed to create article '{article['title']}': {response.status_code} - {response.text}")
            except Exception as e:
                log_warning(f"  Error creating article '{article['title']}': {e}")
            return None

        # Create articles with small delay between each to avoid overwhelming the DB
        article_ids = []
        for art in article_data:
            art_id = await create_article(art)
            if art_id is not None:
                article_ids.append(art_id)
            await asyncio.sleep(0.15)  # Slightly longer delay for articles (larger payloads)

    return article_ids


async def create_article_views_async(
    token: str,
    article_ids: list[int],
    user_ids: dict[str, int],
) -> None:
    """
    Create article views to simulate users reading knowledge base articles.

    Views are recorded by making GET requests to articles (the knowledge service
    automatically tracks views when articles are fetched).
    """
    log_step("Creating article views (async)")
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    try:
        article_views = load_json("user_article_views.json")
    except FileNotFoundError:
        log_warning("  user_article_views.json not found, skipping article views")
        return

    total_views = 0
    success_count = 0

    # Process sequentially with delay to avoid rate limiting
    async with httpx.AsyncClient(follow_redirects=True) as client:
        for view_data in article_views:
            user_key = view_data.get("user_key")
            article_indices = view_data.get("article_indices", [])
            view_counts = view_data.get("view_counts", [])

            if user_key not in user_ids:
                continue

            for i, article_idx in enumerate(article_indices):
                if article_idx >= len(article_ids):
                    continue

                article_id = article_ids[article_idx]
                view_count = view_counts[i] if i < len(view_counts) else 1

                # Record multiple views by fetching the article multiple times
                for _ in range(view_count):
                    try:
                        response = await client.get(
                            f"{ADMIN_WEB_URL}/api/v1/articles/{article_id}",
                            headers=headers,
                        )
                        if response.status_code in (200, 201):
                            success_count += 1
                        total_views += 1
                        # Small delay between requests (removed rate limit delay since DEBUG mode disables rate limiting)
                        await asyncio.sleep(0.01)
                    except Exception:
                        total_views += 1

    log_success(f"  Recorded {success_count}/{total_views} article views across {len(article_views)} users")


async def create_mock_article_attachments(
    token: str,
    article_ids: list[int],
    user_ids: dict[str, int],
) -> None:
    """Upload mock file attachments to knowledge articles."""
    log_step("Creating mock article attachments (async)")
    headers = {"Authorization": f"Bearer {token}"}

    # Varied mock files with different types, sizes, and purposes
    mock_files = [
        # (filename, content_type, size_bytes, description)
        ("Employee_Handbook_2024.pdf", "application/pdf", 245760, "Company handbook with policies"),
        ("Onboarding_Checklist.docx", "application/vnd.openxmlformats-officedocument.wordprocessingml.document", 51200, "Printable checklist version"),
        ("Team_Structure.png", "image/png", 184320, "Org chart diagram"),
        ("Benefits_Overview.pdf", "application/pdf", 153600, "Health insurance and benefits guide"),
        ("Office_Map.jpg", "image/jpeg", 102400, "Office floor plan"),
        ("IT_Setup_Guide.pdf", "application/pdf", 307200, "Technical setup instructions"),
        ("Security_Policy.pdf", "application/pdf", 204800, "Information security guidelines"),
        ("Vacation_Request_Form.docx", "application/vnd.openxmlformats-officedocument.wordprocessingml.document", 25600, "Template for vacation requests"),
        ("Code_Style_Guide.md", "text/markdown", 15360, "Development standards"),
        ("Project_Template.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", 45056, "Project tracking spreadsheet"),
        ("Emergency_Contacts.pdf", "application/pdf", 40960, "Important phone numbers"),
        ("Training_Schedule.ics", "text/calendar", 5120, "Onboarding events calendar"),
        ("Logo_Assets.zip", "application/zip", 512000, "Company logos and brand assets"),
        ("Remote_Access_Guide.pdf", "application/pdf", 176128, "VPN and remote work setup"),
        ("Expense_Report_Template.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", 34816, "Expense submission template"),
        ("Office_Photo.jpg", "image/jpeg", 256000, "Office location photo"),
        ("Meeting_Notes.txt", "text/plain", 2048, "Important meeting notes"),
        ("Architecture_Diagram.png", "image/png", 128000, "System architecture diagram"),
    ]

    # Select articles to attach files to (not all articles get attachments)
    target_article_indices = [0, 1, 2, 4, 5, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24]
    available_indices = [i for i in target_article_indices if i < len(article_ids)]

    # Build list of upload tasks
    upload_tasks = []
    for idx, article_idx in enumerate(available_indices):
        article_id = article_ids[article_idx]
        # Each article gets 1-3 random files
        num_files = min(3, 1 + (idx % 3))
        file_selection = mock_files[idx % len(mock_files): (idx % len(mock_files)) + num_files]
        if len(file_selection) < num_files:
            file_selection = mock_files[:num_files]

        for i, (filename, content_type, file_size, description) in enumerate(file_selection):
            # Generate varied synthetic file content
            content = generate_mock_file_content(filename, content_type, file_size, article_id, i)
            upload_tasks.append((article_id, filename, content, content_type, description, i))

    total_uploads = len(upload_tasks)
    success_count = 0

    async with httpx.AsyncClient(follow_redirects=True) as client:
        async def upload_file(article_id: int, filename: str, content: bytes, content_type: str, description: str, order: int) -> None:
            nonlocal success_count
            try:
                response = await client.post(
                    f"{ADMIN_WEB_URL}/api/v1/attachments/upload",
                    headers=headers,
                    data={
                        "article_id": str(article_id),
                        "description": description,
                        "order": str(order),
                        "is_downloadable": "true",
                    },
                    files={
                        "file": (filename, content, content_type),
                    },
                    timeout=30.0,
                )
                if response.status_code in (200, 201):
                    success_count += 1
                    log_success(f"  Uploaded {filename} to article {article_id}")
                else:
                     log_warning(f"  Failed to upload {filename}: {response.status_code} - {response.text}")
            except Exception as e:
                log_warning(f"  Error uploading {filename}: {e}")

        await asyncio.gather(*[upload_file(article_id, filename, content, content_type, description, i)
                               for article_id, filename, content, content_type, description, i in upload_tasks])

    log_success(f"  Created {success_count}/{total_uploads} article attachments")


def generate_mock_file_content(filename: str, content_type: str, file_size: int, article_id: int, seed: int) -> bytes:
    """Generate synthetic but varied file content."""
    # Create varied content based on file type
    if content_type.startswith("image/"):
        # Minimal valid JPEG header + filler for images
        if content_type == "image/jpeg":
            header = bytes([0xFF, 0xD8, 0xFF, 0xE0, 0x00, 0x10, 0x4A, 0x46, 0x49, 0x46])
        elif content_type == "image/png":
            header = bytes([0x89, 0x50, 0x4E, 0x47, 0x0D, 0x0A, 0x1A, 0x0A])
        else:
            header = b"\x00\x00\x00\x00"
        remaining = max(0, file_size - len(header))
        # Generate pseudo-random filler
        filler = bytes((article_id * 7 + seed * 13 + i * 3) % 256 for i in range(remaining))
        return header + filler
    if content_type == "application/pdf":
        # PDF header
        header = b"%PDF-1.4\n1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n"
        footer = b"\nxref\ntrailer\n<< /Size 1 /Root 1 0 R >>\n%%EOF"
        middle_size = max(0, file_size - len(header) - len(footer))
        middle = bytes((article_id * 11 + seed * 7 + i * 5) % 256 for i in range(middle_size))
        return header + middle + footer
    if content_type == "application/zip":
        # ZIP header
        header = bytes([0x50, 0x4B, 0x03, 0x04])
        remaining = max(0, file_size - len(header))
        filler = bytes((article_id * 3 + seed * 17 + i) % 256 for i in range(remaining))
        return header + filler
    # Text-based files - generate varied content
    base_text = f"Mock content for {filename} (article {article_id}, file {seed})\n"
    base_text += "=" * 50 + "\n"
    base_text += "Generated: Mock file for testing purposes\n"
    base_text += f"Size target: {file_size} bytes\n"
    base_text += f"Content type: {content_type}\n"
    base_text += "-" * 50 + "\n"

    # Add filler to reach target size
    current_len = len(base_text.encode("utf-8"))
    if current_len < file_size:
        lines_needed = (file_size - current_len) // 60 + 1
        for i in range(lines_needed):
            line = f"Line {i + 1}: " + "x" * 40 + f" (seed: {article_id + seed + i})\n"
            base_text += line
            if len(base_text.encode("utf-8")) >= file_size:
                break

    content = base_text.encode("utf-8")[:file_size]
    # Ensure exact size
    if len(content) < file_size:
        content = content + bytes(file_size - len(content))
    return content[:file_size]


async def create_mock_task_attachments(
    token: str,
    user_ids: dict[str, int],
) -> None:
    """Upload mock file attachments to checklist tasks."""
    log_step("Creating mock task attachments (async)")
    headers = {"Authorization": f"Bearer {token}"}

    # Varied task attachment files
    task_files = [
        ("signed_nda.pdf", "application/pdf", 61440, "Signed NDA document"),
        ("id_scan.jpg", "image/jpeg", 81920, "ID document scan"),
        ("diploma.pdf", "application/pdf", 102400, "Education certificate"),
        ("reference_letter.docx", "application/vnd.openxmlformats-officedocument.wordprocessingml.document", 30720, "Recommendation letter"),
        ("medical_certificate.pdf", "application/pdf", 51200, "Health clearance"),
        ("training_completion.pdf", "application/pdf", 71680, "Course completion proof"),
        ("code_sample.py", "text/x-python", 8192, "Programming example"),
        ("project_presentation.pptx", "application/vnd.openxmlformats-officedocument.presentationml.presentation", 153600, "Project deck"),
        ("screenshot_proof.png", "image/png", 122880, "Completion screenshot"),
        ("setup_confirmation.txt", "text/plain", 1024, "Setup verification"),
        ("payroll_form.xls", "application/vnd.ms-excel", 22528, "Payroll information form"),
        ("contract.doc", "application/msword", 40960, "Employment contract"),
        ("benefits_form.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", 18432, "Benefits enrollment"),
        ("profile_photo.jpeg", "image/jpeg", 98304, "Employee photo"),
    ]

    async with httpx.AsyncClient(follow_redirects=True) as client:
        # First, get some checklists with tasks to attach files to
        try:
            response = await client.get(
                f"{ADMIN_WEB_URL}/api/v1/checklists/",
                headers={**headers, "Content-Type": "application/json"},
                params={"skip": 0, "limit": 20},
            )
            if response.status_code != 200:
                log_warning(f"Could not fetch checklists: {response.status_code}")
                return

            checklists = response.json().get("checklists", [])
        except Exception as e:
            log_warning(f"Error fetching checklists: {e}")
            return

        # Fetch tasks for all checklists in parallel
        async def fetch_checklist_tasks(checklist: dict) -> tuple[dict, list]:
            checklist_id = checklist["id"]
            try:
                response = await client.get(
                    f"{ADMIN_WEB_URL}/api/v1/tasks/checklist/{checklist_id}",
                    headers={**headers, "Content-Type": "application/json"},
                )
                if response.status_code == 200:
                    return (checklist, response.json())
                return (checklist, [])
            except Exception:
                return (checklist, [])

        checklist_task_pairs = await asyncio.gather(*[fetch_checklist_tasks(checklist) for checklist in checklists[:12]])

        # Build list of upload tasks
        upload_tasks = []
        for checklist_idx, (checklist, tasks) in enumerate(checklist_task_pairs):
            if not tasks:
                continue
            checklist_id = checklist["id"]

            # Select 1-2 tasks to attach files to
            num_tasks = 1 + (checklist_idx % 2)
            selected_tasks = tasks[:num_tasks] if len(tasks) >= num_tasks else tasks

            for task_idx, task in enumerate(selected_tasks):
                task_id = task["id"]
                # Select varied file(s) for this task
                file_idx = (checklist_idx * 3 + task_idx) % len(task_files)
                filename, content_type, file_size, description = task_files[file_idx]

                # Generate mock content
                content = generate_mock_file_content(filename, content_type, file_size, task_id, task_idx)
                upload_tasks.append((task_id, filename, content, content_type, description))

                # Occasionally add a second file (30% chance)
                if checklist_idx % 3 == 0 and task_idx == 0:
                    second_file_idx = (file_idx + 1) % len(task_files)
                    filename2, content_type2, file_size2, desc2 = task_files[second_file_idx]
                    content2 = generate_mock_file_content(filename2, content_type2, file_size2, task_id, task_idx + 10)
                    upload_tasks.append((task_id, filename2, content2, content_type2, desc2))

        total_uploads = len(upload_tasks)
        success_count = 0

        async def upload_file(task_id: int, filename: str, content: bytes, content_type: str, description: str) -> None:
            nonlocal success_count
            try:
                response = await client.post(
                    f"{ADMIN_WEB_URL}/api/v1/tasks/{task_id}/attachments",
                    headers=headers,
                    data={"description": description},
                    files={
                        "file": (filename, content, content_type),
                    },
                    timeout=30.0,
                )
                if response.status_code in (200, 201):
                    success_count += 1
                    log_success(f"  Uploaded {filename} to task {task_id}")
                else:
                    log_warning(f"  Failed to upload {filename} to task {task_id}: {response.status_code} - {response.text}")
            except Exception as e:
                log_warning(f"  Error uploading {filename} to task {task_id}: {e}")

        await asyncio.gather(*[upload_file(task_id, filename, content, content_type, description)
                               for task_id, filename, content, content_type, description in upload_tasks])

    log_success(f"  Created {success_count}/{total_uploads} task attachments")


async def create_dialogue_scenarios(
    token: str,
    scenario_data: list[dict],
) -> None:
    """Create dialogue scenarios with steps."""
    log_step("Creating dialogue scenarios with steps")
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    async with httpx.AsyncClient(follow_redirects=True) as client:
        async def create_scenario(scenario: dict) -> None:
            scenario_title = scenario["title"]
            try:
                response = await client.post(
                    f"{ADMIN_WEB_URL}/api/v1/dialogue-scenarios/",
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

        # Create scenarios with small delay between each to avoid overwhelming the DB
        for scenario in scenario_data:
            await create_scenario(scenario)
            await asyncio.sleep(0.1)  # Small delay between requests


async def create_meeting_templates(
    token: str,
    dept_ids: dict[str, int],
    meeting_data: list[dict],
) -> list[int]:
    """Create meeting templates."""
    log_step("Creating meeting templates")
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    async with httpx.AsyncClient(follow_redirects=True) as client:
        async def create_meeting(meeting: dict) -> int | None:
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
                    f"{ADMIN_WEB_URL}/api/v1/meetings/",
                    headers=headers,
                    json=meet_payload,
                )
                if response.status_code in (200, 201):
                    meet_data = response.json()
                    meet_id = meet_data["id"]
                    log_success(f"  Meeting '{meeting['title']}' created (ID: {meet_id})")
                    return meet_id
                log_warning(f"  Failed to create meeting '{meeting['title']}': {response.status_code} - {response.text}")
            except Exception as e:
                log_warning(f"  Error creating meeting '{meeting['title']}': {e}")
            return None

        results = await asyncio.gather(*[create_meeting(meet) for meet in meeting_data])
        meeting_ids = [meet_id for meet_id in results if meet_id is not None]

    return meeting_ids


async def create_user_meetings_async(
    token: str,
    meeting_template_ids: list[int],
    user_ids: dict[str, int],
) -> None:
    """Create all user meetings asynchronously."""
    log_step("Creating user meetings (async)")

    user_meetings_data = load_json("user_meetings.json")

    async def create_single_meeting(meeting: dict) -> None:
        user_key = meeting.get("user_key")
        status = meeting.get("status")
        days_ago = meeting.get("days_ago", 0)

        if user_key in user_ids:
            await create_user_meetings(
                token,
                meeting_template_ids,
                user_ids[user_key],
                days_ago,
                status,
            )

    await asyncio.gather(*[create_single_meeting(m) for m in user_meetings_data])


async def create_user_meetings(
    token: str,
    meeting_template_ids: list[int],
    user_id: int,
    scheduled_days_ago: int = 0,
    status: str = "SCHEDULED",
) -> None:
    """Create user meeting instances."""
    if not meeting_template_ids:
        return

    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    # Use only first 3 templates per user to avoid duplicates
    templates_to_assign = meeting_template_ids[:3]

    async with httpx.AsyncClient(follow_redirects=True) as client:
        for idx, meet_tpl_id in enumerate(templates_to_assign):
            # For SCHEDULED: use future date (1-7 days ahead)
            # For COMPLETED/MISSED/CANCELLED: schedule in future then update status
            if status == "SCHEDULED":
                # Vary the scheduled time slightly to avoid exact duplicates
                days_ahead = max(1, 7 - scheduled_days_ago + idx)
                scheduled_at = datetime.now() + timedelta(days=days_ahead, hours=idx * 2)
            else:
                # Schedule in near future then update status to simulate historical meeting
                scheduled_at = datetime.now() + timedelta(days=1, hours=idx)

            try:
                response = await client.post(
                    f"{ADMIN_WEB_URL}/api/v1/user-meetings/assign",
                    headers=headers,
                    json={
                        "user_id": user_id,
                        "meeting_id": meet_tpl_id,
                        "scheduled_at": scheduled_at.isoformat(),
                    },
                )

                if response.status_code in (200, 201):
                    user_meeting = response.json()
                    user_meeting_id = user_meeting["id"]
                    log_success(f"  User meeting {user_meeting_id} created (status: {status})")

                    if status in ["COMPLETED", "MISSED", "CANCELLED"]:
                        await client.patch(
                            f"{ADMIN_WEB_URL}/api/v1/user-meetings/{user_meeting_id}",
                            headers=headers,
                            json={"status": status},
                        )
                elif response.status_code == 409:
                    # Meeting already assigned - skip silently
                    pass
                else:
                     log_warning(f"  Failed to create user meeting: {response.status_code} - {response.text[:200]}")

            except Exception as e:
                log_warning(f"  Error creating user meeting: {e}")


async def create_notifications_async(
    token: str,
    user_ids: list[int],
    notification_data: list[dict],
) -> None:
    """Create all notifications asynchronously."""
    log_step("Creating notifications (async)")
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {token}"}

    async with httpx.AsyncClient(follow_redirects=True) as client:

        async def send_notification(notif: dict, user_id: int) -> None:
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
                    f"{ADMIN_WEB_URL}/api/v1/notifications/send",
                    headers=headers,
                    json=notif_payload,
                )
                if response.status_code in (200, 201):
                    log_success(f"  Notification sent to user {user_id}")
                else:
                    log_warning(
                        f"  Failed to send notification to user {user_id}: {response.status_code} {response.text[:200]}"
                    )
            except Exception as e:
                log_warning(f"  Error sending notification: {e}")

        tasks = [
            send_notification(notif, user_id)
            for notif in notification_data
            for user_id in user_ids[:3]
        ]

        await asyncio.gather(*tasks)


async def create_escalations_async(
    token: str,
    user_ids: list[int],
    escalation_data: list[dict],
) -> None:
    """Create all escalations asynchronously."""
    log_step("Creating escalations (async)")
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {token}"}

    async with httpx.AsyncClient(follow_redirects=True) as client:

        async def create_single_escalation(esc: dict, idx: int) -> None:
            user_id = user_ids[idx % len(user_ids)] if user_ids else None
            if not user_id:
                return

            esc_payload = {
                "user_id": user_id,
                "type": esc.get("type", "GENERAL"),
                "source": esc.get("source", "MANUAL"),
                "reason": esc.get("reason"),
                "context": esc.get("context", {}),
                "related_entity_type": esc.get("related_entity_type"),
                "related_entity_id": esc.get("related_entity_id"),
            }

            try:
                response = await client.post(
                    f"{ADMIN_WEB_URL}/api/v1/escalations/",
                    headers=headers,
                    json=esc_payload,
                )
                if response.status_code in (200, 201):
                    escalation = response.json()
                    esc_id = escalation["id"]

                    status = esc.get("status", "PENDING")
                    if status != "PENDING":
                        await client.patch(
                            f"{ADMIN_WEB_URL}/api/v1/escalations/{esc_id}",
                            headers=headers,
                            json={"status": status},
                        )

                    log_success(f"  Escalation {esc_id} created (status: {status})")
                else:
                     log_warning(f"  Failed to create escalation: {response.status_code} - {response.text[:200]}")
            except Exception as e:
                log_warning(f"  Error creating escalation: {e}")

        tasks = [create_single_escalation(esc, i) for i, esc in enumerate(escalation_data)]
        await asyncio.gather(*tasks)


async def create_feedback_async(
    token: str,
    user_ids: dict[str, int],
    feedback_data: dict,
) -> None:
    """Create all feedback asynchronously."""
    log_step("Creating feedback (async)")
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    service_headers = {"X-Service-Api-Key": SERVICE_API_KEY, "Content-Type": "application/json"}

    async with httpx.AsyncClient(follow_redirects=True) as client:
        pulse_data = feedback_data.get("pulse_surveys", [])
        exp_data = feedback_data.get("experience_ratings", [])
        comment_data = feedback_data.get("comments", [])

        async def create_pulse(pulse: dict) -> None:
            user_key = pulse.get("user_key")
            user_id = user_ids.get(user_key) if user_key else None
            
            # Make all feedback non-anonymous to avoid department_id/level requirement
            payload = {
                "user_id": user_id,
                "rating": pulse.get("rating", 7),
                "is_anonymous": False,  # Force non-anonymous for now
            }
            
            try:
                response = await client.post(
                    f"{ADMIN_WEB_URL}/api/v1/feedback/pulse",
                    headers=service_headers,
                    json=payload,
                )
                if response.status_code in (200, 201):
                    user_info = f"user {user_id}" if user_id else "anonymous"
                    log_success(f"  Pulse survey created for {user_info} (rating: {payload['rating']})")
                else:
                    log_warning(f"  Failed to create pulse survey: {response.status_code} - {response.text[:100]}")
            except Exception as e:
                log_warning(f"  Error creating pulse survey: {e}")

        async def create_experience(exp: dict) -> None:
            user_key = exp.get("user_key")
            user_id = user_ids.get(user_key) if user_key else None
            
            # Make all feedback non-anonymous to avoid department_id/level requirement
            payload = {
                "user_id": user_id,
                "rating": exp.get("rating", 4),
                "is_anonymous": False,  # Force non-anonymous for now
            }
            
            try:
                response = await client.post(
                    f"{ADMIN_WEB_URL}/api/v1/feedback/experience",
                    headers=service_headers,
                    json=payload,
                )
                if response.status_code in (200, 201):
                    user_info = f"user {user_id}" if user_id else "anonymous"
                    log_success(f"  Experience rating created for {user_info} (rating: {payload['rating']})")
                else:
                    log_warning(f"  Failed to create experience rating: {response.status_code} - {response.text[:100]}")
            except Exception as e:
                log_warning(f"  Error creating experience rating: {e}")

        async def create_comment(comment: dict) -> None:
            user_key = comment.get("user_key")
            user_id = user_ids.get(user_key) if user_key else None
            
            # Make all feedback non-anonymous to avoid department_id/level requirement
            payload = {
                "user_id": user_id,
                "comment": comment.get("comment", "Great experience!"),
                "is_anonymous": False,  # Force non-anonymous for now
                "allow_contact": comment.get("allow_contact", False),
                "contact_email": comment.get("contact_email"),
            }
            
            try:
                response = await client.post(
                    f"{ADMIN_WEB_URL}/api/v1/feedback/comments",
                    headers=service_headers,
                    json=payload,
                )
                if response.status_code in (200, 201):
                    user_info = f"user {user_id}" if user_id else "anonymous"
                    log_success(f"  Comment created for {user_info}")
                else:
                    log_warning(f"  Failed to create comment: {response.status_code} - {response.text[:100]}")
            except Exception as e:
                log_warning(f"  Error creating comment: {e}")

        # Create feedback with small delay to avoid overwhelming the service
        for pulse in pulse_data:
            await create_pulse(pulse)
            await asyncio.sleep(0.05)

        for exp in exp_data:
            await create_experience(exp)
            await asyncio.sleep(0.05)

        for comment in comment_data:
            await create_comment(comment)
            await asyncio.sleep(0.05)


async def create_pending_invitations_async(
    token: str,
    dept_ids: dict[str, int],
    mentor_id: int | None = None,
) -> None:
    """Create pending invitations asynchronously."""
    log_step("Creating pending invitations (async)")
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    pending_invitations = load_json("pending_invitations.json")

    async with httpx.AsyncClient(follow_redirects=True) as client:

        async def create_invitation(inv: dict) -> None:
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
                    f"{ADMIN_WEB_URL}/api/v1/invitations/",
                    headers=headers,
                    json=inv_payload,
                )
                if response.status_code in (200, 201):
                    inv_data = response.json()
                    log_success(
                        f"  Pending invitation created: {inv['email']} (token: {inv_data.get('token', 'N/A')[:20]}...)"
                    )
                else:
                     log_warning(f"  Failed to create pending invitation: {response.status_code} - {response.text}")
            except Exception as e:
                log_warning(f"  Error creating pending invitation: {e}")

        await asyncio.gather(*[create_invitation(inv) for inv in pending_invitations])


async def create_user_mentors_async(
    token: str,
    user_ids: dict[str, int],
) -> None:
    """Create user-mentor relationships asynchronously."""
    log_step("Creating user-mentor relationships (async)")
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    user_mentors_data = load_json("user_mentors.json")

    async with httpx.AsyncClient(follow_redirects=True) as client:

        async def create_relation(rel: dict) -> None:
            user_key = rel.get("user_key")
            mentor_key = rel.get("mentor_key")

            if user_key not in user_ids or mentor_key not in user_ids:
                log_warning(f"  Skipping relation: user or mentor not found ({user_key} -> {mentor_key})")
                return

            user_id = user_ids[user_key]
            mentor_id = user_ids[mentor_key]

            payload = {
                "user_id": user_id,
                "mentor_id": mentor_id,
                "notes": rel.get("notes"),
            }

            try:
                response = await client.post(
                    f"{ADMIN_WEB_URL}/api/v1/user-mentors/",
                    headers=headers,
                    json=payload,
                )
                if response.status_code in (200, 201):
                    log_success(f"  Mentor assigned: {user_key} -> {mentor_key}")
                else:
                     log_warning(f"  Failed to assign mentor {mentor_key} to {user_key}: {response.status_code} - {response.text}")
            except Exception as e:
                log_warning(f"  Error assigning mentor {mentor_key} to {user_key}: {e}")

        await asyncio.gather(*[create_relation(rel) for rel in user_mentors_data])


async def main(skip_services: list[str] | None = None, dry_run: bool = False) -> None:
    """Run mock data setup across all services with optional dry-run mode."""
    skip_services = skip_services or []

    log_divider()
    log_step("Mock Data Setup for Mentor Bot - Rich Demo Data")
    log_divider()

    if dry_run:
        log_warning("Running in DRY-RUN mode - no data will be created")

    log_info(f"Routing all API calls through {ADMIN_WEB_URL}")

    if not await wait_for_admin_web(ADMIN_WEB_URL):
        log_error("admin_web is not available. Exiting.")
        sys.exit(1)

    if not dry_run and not create_admin_user():
        # Non-fatal: in prod the admin is typically pre-seeded and the host
        # has no docker/psql access. If login below fails, we'll exit then.
        log_warning("Could not bootstrap admin user; assuming it already exists.")

    token = await get_admin_token()
    if not token:
        log_error("Failed to get admin token. Exiting.")
        sys.exit(1)

    log_divider()
    log_step("Creating mock data - Rich Demo Dataset")
    log_divider()

    dept_ids = await create_departments(token)

    users_data = load_json("users.json")
    user_ids, mentor_ids, hr_ids = await create_all_users_async(token, dept_ids)

    # Create user-mentor relationships
    await create_user_mentors_async(token, user_ids)

    template_ids: list[int] = []

    if "checklists" not in skip_services:
        templates = load_json("templates.json")
        template_ids = await create_checklist_templates(token, dept_ids, templates)
        await create_checklist_instances_async(
            token,
            template_ids,
            users_data,
            user_ids,
            mentor_ids[0] if mentor_ids else None,
            hr_ids[0] if hr_ids else None,
        )

        # Create mock file attachments for tasks
        await create_mock_task_attachments(token, user_ids)

    meeting_template_ids: list[int] = []
    if "meeting" not in skip_services:
        meetings = load_json("meetings.json")
        meeting_template_ids = await create_meeting_templates(token, dept_ids, meetings)
        await create_user_meetings_async(token, meeting_template_ids, user_ids)

    if "notification" not in skip_services:
        notifications = load_json("notifications.json")
        await create_notifications_async(token, list(user_ids.values()), notifications)

    if "escalation" not in skip_services:
        escalations = load_json("escalations.json")
        await create_escalations_async(token, list(user_ids.values()), escalations)

    if "feedback" not in skip_services:
        feedback = load_json("feedback.json")
        await create_feedback_async(token, user_ids, feedback)

    article_ids: list[int] = []
    if "knowledge" not in skip_services:
        categories = load_json("knowledge_categories.json")
        cat_ids = await create_knowledge_categories(token, dept_ids, categories)

        tags = load_json("knowledge_tags.json")
        tag_ids = await create_knowledge_tags(token, tags)

        articles = load_json("knowledge_articles.json")
        article_ids = await create_knowledge_articles(token, cat_ids, tag_ids, dept_ids, articles)

        scenarios = load_json("dialogue_scenarios.json")
        await create_dialogue_scenarios(token, scenarios)

        # Create article views for users
        await create_article_views_async(token, article_ids, user_ids)

        # Create mock file attachments for articles
        await create_mock_article_attachments(token, article_ids, user_ids)

    await create_pending_invitations_async(token, dept_ids, mentor_ids[0] if mentor_ids else None)

    log_divider()
    log_success("Mock data setup completed successfully!")
    log_divider()
    log_info("Summary:")
    log_info(f"  Departments:      {len(dept_ids)}")
    log_info(f"  Users:             {len(user_ids)}")
    log_info("  - Admins:          1")
    log_info(f"  - HR:              {len(hr_ids)}")
    log_info(f"  - Mentors:         {len(mentor_ids)}")
    log_info("  - Newbies:         12")
    log_info("  - Employees:       8")
    if "checklists" not in skip_services:
        checklist_instances = load_json("checklist_instances.json")
        log_info(f"  Templates:         {len(templates)}")
        log_info(f"  Checklist instances: {len(checklist_instances)} (diverse completion: 0%, 25%, 50%, 75%, 100%)")
        log_info("  Task attachments:  Various files (PDFs, docs, images, etc.)")
    if "knowledge" not in skip_services:
        categories = load_json("knowledge_categories.json")
        tags = load_json("knowledge_tags.json")
        articles = load_json("knowledge_articles.json")
        scenarios = load_json("dialogue_scenarios.json")
        article_views = load_json("user_article_views.json")
        total_views = sum(sum(v.get("view_counts", [])) for v in article_views)
        log_info(f"  Categories:        {len(categories)}")
        log_info(f"  Tags:              {len(tags)}")
        log_info(f"  Articles:          {len(articles)}")
        log_info(f"  Article views:     {total_views} (users with varied reading activity)")
        log_info("  Article attachments: Various files (PDFs, docs, images, spreadsheets)")
        log_info(f"  Dialogue scenarios: {len(scenarios)}")
    if "meeting" not in skip_services:
        meetings = load_json("meetings.json")
        log_info(f"  Meeting templates: {len(meetings)}")
        log_info("  User meetings:     8 (COMPLETED, SCHEDULED, MISSED, CANCELLED)")
    if "escalation" not in skip_services:
        escalations = load_json("escalations.json")
        log_info(f"  Escalations:       {len(escalations)} (PENDING, ASSIGNED, IN_PROGRESS, RESOLVED, REJECTED)")
    if "feedback" not in skip_services:
        feedback = load_json("feedback.json")
        pulse_count = len(feedback.get("pulse_surveys", []))
        exp_count = len(feedback.get("experience_ratings", []))
        comment_count = len(feedback.get("comments", []))
        log_info(f"  Feedback entries:  {pulse_count} pulse, {exp_count} experience, {comment_count} comments")
    user_mentors = load_json("user_mentors.json")
    log_info(f"  User-Mentor relations: {len(user_mentors)}")
    log_divider()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Setup mock data for Mentor Bot")
    parser.add_argument(
        "--admin-web-url",
        type=str,
        default=None,
        help="Base URL of the admin_web app (default: $ADMIN_WEB_URL or http://localhost:3000)",
    )
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
    if args.admin_web_url:
        ADMIN_WEB_URL = args.admin_web_url.rstrip("/")
    skip_list = [s.strip() for s in args.skip_services.split(",") if s.strip()]

    asyncio.run(main(skip_services=skip_list, dry_run=args.dry_run))
