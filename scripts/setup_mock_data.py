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
import logging
import os
import subprocess
import sys
from collections.abc import Callable
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

import httpx

logger = logging.getLogger(__name__)

SCRIPT_DIR = Path(__file__).parent
MOCK_DATA_DIR = SCRIPT_DIR / "mock_data"


# This script is host-side: service URLs in .env (e.g. http://auth_service:8000)
# only resolve inside the docker network, so we ignore them here. We pick up
# DB credentials needed to bootstrap the admin user via psql, and ADMIN_WEB_URL
# for routing all API calls through the admin_web proxy.
_REQUIRED_ENV_VARS = [
    "POSTGRES_USER",
    "POSTGRES_PASSWORD",
    "ADMIN_EMAIL",
    "ADMIN_PASSWORD",
    "SERVICE_API_KEY",
    "ADMIN_WEB_URL",
    "AUTH_SERVICE_URL",
    "MOCK_DATA_CHECKLIST_CONCURRENCY",
]


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
        if key not in _REQUIRED_ENV_VARS:
            continue
        os.environ.setdefault(key, value.strip().strip('"').strip("'"))


_load_env_file()

# Single entry point: admin_web proxies /api/v1/<service>/... to the right backend.
ADMIN_WEB_URL = os.getenv("ADMIN_WEB_URL", "http://localhost:3000").rstrip("/")


def _get_positive_int_env(name: str, default: int) -> int:
    """Read a positive integer from the environment."""
    value = os.getenv(name)
    if not value:
        return default
    try:
        parsed = int(value)
    except ValueError:
        print(f"[WARNING] Invalid {name}={value!r}; using {default}")
        return default
    if parsed < 1:
        print(f"[WARNING] Invalid {name}={value!r}; using {default}")
        return default
    return parsed


MOCK_DATA_CHECKLIST_CONCURRENCY = _get_positive_int_env("MOCK_DATA_CHECKLIST_CONCURRENCY", 2)


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


_success_dots_open = False


def _close_success_dots() -> None:
    """Finish the current success-dot line if one is active."""
    global _success_dots_open
    if _success_dots_open:
        print()
        _success_dots_open = False


def log_info(msg: str) -> None:
    """Print info message to console."""
    _close_success_dots()
    print(f"{Colors.CYAN}[INFO]{Colors.NC} {msg}")


def log_success(msg: str) -> None:
    """Print success message to console as green dots."""
    global _success_dots_open
    print(f"{Colors.GREEN}.{Colors.NC}", end="", flush=True)
    _success_dots_open = True


def log_success_newline() -> None:
    """Print a newline after success dots, once."""
    _close_success_dots()


def log_warning(msg: str) -> None:
    """Print warning message to console."""
    _close_success_dots()
    print(f"{Colors.YELLOW}[WARNING]{Colors.NC} {msg}")


def log_error(msg: str) -> None:
    """Print error message to console."""
    _close_success_dots()
    print(f"{Colors.RED}[ERROR]{Colors.NC} {msg}")


def log_step(msg: str) -> None:
    """Print step message to console."""
    _close_success_dots()
    print(f"{Colors.BLUE}>>>{Colors.NC} {Colors.BOLD}{msg}{Colors.NC}")


def log_divider() -> None:
    """Print divider line to console."""
    _close_success_dots()
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
            return True

        if result.returncode != 0:
            error = result.stderr.strip()
            log_warning(f"Existence check via docker failed: {error}")
            if 'relation "users" does not exist' in error:
                return False
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
            return True
        log_warning(f"Failed to create admin: {result.stderr.strip()}")
    except FileNotFoundError:
        log_warning("docker compose not found, trying direct psql")
        return create_admin_user_direct()
    except Exception as e:
        log_warning(f"Error creating admin user: {e}")
        return False
    else:
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
            return True
        log_warning(f"Failed to create admin: {result.stderr.strip()}")
    except Exception as e:
        log_warning(f"Error creating admin user: {e}")
        return False
    else:
        return False


async def wait_for_admin_web(url: str, max_attempts: int = 30, delay: int = 1) -> bool:
    """
    Wait for admin_web to become reachable.

    Check if admin_web responds at all (any status code means the app is up).
    """
    log_step(f"Waiting for admin_web at {url}")
    async with httpx.AsyncClient(timeout=5.0, follow_redirects=False) as client:
        for attempt in range(1, max_attempts + 1):
            try:
                response = await client.get(f"{url}")
                # Any response (even 404) means the app is up and proxy is working
                return True
            except Exception as e:
                logger.debug("Admin_web not ready yet: %s", e)
            log_warning(f"Attempt {attempt}/{max_attempts}: admin_web not ready yet {url}")
            await asyncio.sleep(delay)
    log_error(f"admin_web failed to respond after {max_attempts} attempts")
    return False


async def wait_for_auth_service(max_attempts: int = 60, delay: int = 1) -> bool:
    """Wait until auth_service is reachable through the admin_web proxy."""
    log_step("Waiting for auth_service through admin_web")
    login_url = f"{ADMIN_WEB_URL}/api/v1/auth/login"
    async with httpx.AsyncClient(timeout=5.0, follow_redirects=False) as client:
        for attempt in range(1, max_attempts + 1):
            try:
                response = await client.post(
                    login_url,
                    data={
                        "username": ADMIN_EMAIL,
                        "password": ADMIN_PASSWORD,
                        "grant_type": "password",
                    },
                    headers={"Content-Type": "application/x-www-form-urlencoded"},
                )
                if response.status_code not in {502, 503, 504}:
                    return True
            except Exception as e:
                logger.debug("Auth service not ready yet: %s", e)
            log_warning(f"Attempt {attempt}/{max_attempts}: auth_service not ready yet")
            await asyncio.sleep(delay)
    log_error(f"auth_service failed to respond after {max_attempts} attempts")
    return False


async def get_admin_token() -> str | None:
    """Get admin authentication token."""
    log_step("Getting admin authentication token")
    return await login_user(ADMIN_EMAIL, ADMIN_PASSWORD)


async def login_user(email: str, password: str) -> str | None:
    """Log in a user and return an access token."""
    async with httpx.AsyncClient(follow_redirects=True) as client:
        try:
            response = await client.post(
                f"{ADMIN_WEB_URL}/api/v1/auth/login",
                data={
                    "username": email,
                    "password": password,
                    "grant_type": "password",
                },
                headers={"Content-Type": "application/x-www-form-urlencoded"},
            )
            if response.status_code == 200:
                data = response.json()
                token = data.get("access_token")
                if token:
                    return token
            log_warning(f"  Failed to log in '{email}': {response.status_code} - {response.text[:200]}")
        except Exception as e:
            log_warning(f"  Failed to connect to auth service for '{email}': {e}")
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
        log_success_newline()

    dept_ids = {name: dept_id for name, dept_id in results if dept_id is not None}
    return dept_ids


async def fetch_existing_departments(token: str) -> dict[str, int]:
    """Fetch existing departments from the API."""
    log_step("Fetching existing departments")
    departments = load_json("departments.json")
    dept_ids: dict[str, int] = {}
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    async with httpx.AsyncClient(follow_redirects=True) as client:
        for dept in departments:
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
                        dept_ids[name] = dept_id
                        log_success("")
            except Exception as e:
                log_warning(f"  Error fetching department '{name}': {e}")
        log_success_newline()

    return dept_ids


async def _create_or_get_department(
    client: httpx.AsyncClient,
    headers: dict[str, str],
    dept: dict,
) -> tuple[str, int | None]:
    """Create a department via auth API or return existing ID. Auth service syncs to other services."""
    name = dept["name"]
    try:
        response = await client.post(
            f"{ADMIN_WEB_URL}/api/v1/departments/",
            headers=headers,
            json=dept,
        )
        if response.status_code in (200, 201):
            dept_id = response.json()["id"]
            log_success("")
            return name, dept_id
        if response.status_code == 409:
            # Department already exists, try to get its ID
            response = await client.get(
                f"{ADMIN_WEB_URL}/api/v1/departments/",
                headers=headers,
                params={"search": name},
            )
            if response.status_code == 200:
                existing = response.json().get("departments", [])
                if existing:
                    dept_id = existing[0]["id"]
                    log_warning(f"  Failed to create department '{name}': 409 - {response.text}")
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
            log_success("")
            return (user_data.get("key", ""), user_id)

        response = await client.post(
            f"{ADMIN_WEB_URL}/api/v1/users/",
            headers=headers,
            json=user_payload,
        )
        if response.status_code in (200, 201):
            user_id = response.json()["id"]
            log_success("")
            return (user_data.get("key", ""), user_id)
        if response.status_code == 409:
            # User already exists, try to get ID by email
            response = await client.get(
                f"{ADMIN_WEB_URL}/api/v1/users/by-email/{user_data['email']}",
                headers=headers,
            )
            if response.status_code == 200:
                user_id = response.json()["id"]
                log_success("")
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

    async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
        tasks = [create_user(client, token, user, dept_ids) for user in enriched_users]
        results = await asyncio.gather(*tasks)
        log_success_newline()

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

    return user_ids, mentor_ids, hr_ids


async def fetch_existing_users(
    token: str,
    dept_ids: dict[str, int],
    users_data: dict,
) -> tuple[dict[str, int], list[int], list[int]]:
    """Fetch existing users from the API."""
    log_step("Fetching existing users")
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    user_ids: dict[str, int] = {}
    mentor_ids: list[int] = []
    hr_ids: list[int] = []

    async with httpx.AsyncClient(follow_redirects=True) as client:
        for key, user in users_data.items():
            try:
                response = await client.get(
                    f"{ADMIN_WEB_URL}/api/v1/users/by-email/{user['email']}",
                    headers=headers,
                )
                if response.status_code == 200:
                    user_id = response.json()["id"]
                    user_ids[key] = user_id
                    if user.get("role") == "MENTOR":
                        mentor_ids.append(user_id)
                    elif user.get("role") in ["HR", "ADMIN"]:
                        hr_ids.append(user_id)
                    log_success("")
                else:
                    log_warning(
                        f"  User '{user['email']}' not found (status {response.status_code}): {response.text[:100]}"
                    )
            except Exception as e:
                log_warning(f"  Error fetching user '{user['email']}': {e}")
        log_success_newline()

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
                    log_success("")

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
                        log_success("")

                    return tpl_id
                log_warning(f"  Failed to create template '{tpl_name}': {response.status_code} - {response.text}")
            except Exception as e:
                log_warning(f"  Error creating template '{tpl_name}': {e}")
            return None

        results = await asyncio.gather(*[create_template(tpl) for tpl in template_data])
        log_success_newline()
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
    created_count = 0
    semaphore = asyncio.Semaphore(MOCK_DATA_CHECKLIST_CONCURRENCY)

    async def create_single_instance(instance: dict) -> None:
        nonlocal created_count
        async with semaphore:
            newbie_key = instance.get("user_key")
            status = instance.get("status")
            days_ago = instance.get("days_ago", 0)
            completed_tasks = instance.get("completed_tasks", 0)
            template_index = instance.get("template_index", 0)

            if newbie_key in user_ids:
                result = await create_checklist_instances(
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
                if result:
                    created_count += 1

    await asyncio.gather(*[create_single_instance(inst) for inst in checklist_instances])
    if created_count > 0:
        log_success_newline()


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
                log_success(
                    f"  Checklist {checklist_id} created for user {user_id} (status: {status}, template: {template_index})"
                )

                if completed_task_count > 0 and status != "COMPLETED":
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
                        log_success("")
                    else:
                        log_warning(
                            f"  Failed to complete checklist {checklist_id}: {complete_resp.status_code} - {complete_resp.text}"
                        )

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
                    log_success("")
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

    if cat_ids:
        log_success_newline()
    return cat_ids


async def fetch_existing_categories(
    token: str,
    dept_ids: dict[str, int],
    category_data: list[dict],
) -> dict[str, int]:
    """Fetch existing knowledge base categories."""
    log_step("Fetching existing categories")
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    cat_ids: dict[str, int] = {}

    async with httpx.AsyncClient(follow_redirects=True) as client:
        # Fetch all categories first
        try:
            response = await client.get(
                f"{ADMIN_WEB_URL}/api/v1/categories/",
                headers=headers,
            )
            if response.status_code == 200:
                all_categories = response.json()
                # Handle both list and paginated response formats
                if isinstance(all_categories, dict) and "categories" in all_categories:
                    all_categories = all_categories["categories"]
                if isinstance(all_categories, list):
                    # Create a mapping of name to id
                    cat_map = {cat["name"]: cat["id"] for cat in all_categories}
                    # Match with our category data
                    for cat in category_data:
                        slug = cat["slug"]
                        if cat["name"] in cat_map:
                            cat_ids[slug] = cat_map[cat["name"]]
                            log_success("")
        except Exception as e:
            log_warning(f"  Error fetching categories: {e}")

    if cat_ids:
        log_success_newline()
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
                    log_success("")
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

    if tag_ids:
        log_success_newline()
    return tag_ids


async def fetch_existing_tags(
    token: str,
    tag_data: list[dict],
) -> dict[str, int]:
    """Fetch existing knowledge base tags."""
    log_step("Fetching existing tags")
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    tag_ids: dict[str, int] = {}

    async with httpx.AsyncClient(follow_redirects=True) as client:
        for tag in tag_data:
            slug = tag["slug"]
            try:
                response = await client.get(
                    f"{ADMIN_WEB_URL}/api/v1/tags/",
                    headers=headers,
                    params={"search": tag["name"]},
                )
                if response.status_code == 200:
                    tags = response.json()
                    if tags:
                        tag_id = tags[0]["id"]
                        tag_ids[slug] = tag_id
                        log_success("")
            except Exception as e:
                log_warning(f"  Error fetching tag '{tag['name']}': {e}")
            await asyncio.sleep(0.05)

    if tag_ids:
        log_success_newline()
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
                    article_resp = response.json()
                    art_id = article_resp["id"]
                    log_success(
                        f"  Article '{article['title']}' created (ID: {art_id}, status: {article.get('status')})"
                    )
                    return art_id
                log_warning(
                    f"  Failed to create article '{article['title']}': {response.status_code} - {response.text}"
                )
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

    if article_ids:
        log_success_newline()
    return article_ids


async def fetch_existing_articles(
    token: str,
    cat_ids: dict[str, int],
    tag_ids: dict[str, int],
    dept_ids: dict[str, int],
    article_data: list[dict],
) -> list[int]:
    """Fetch existing knowledge base articles."""
    log_step("Fetching existing articles")
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    article_ids: list[int] = []

    async with httpx.AsyncClient(follow_redirects=True) as client:
        # Fetch all articles first
        try:
            response = await client.get(
                f"{ADMIN_WEB_URL}/api/v1/articles/",
                headers=headers,
            )
            if response.status_code == 200:
                all_articles = response.json()
                # Handle both list and paginated response formats
                if isinstance(all_articles, dict) and "articles" in all_articles:
                    all_articles = all_articles["articles"]
                if isinstance(all_articles, list):
                    # Create a mapping of title to id
                    article_map = {art["title"]: art["id"] for art in all_articles}
                    # Match with our article data
                    for article in article_data:
                        if article["title"] in article_map:
                            article_ids.append(article_map[article["title"]])
                            log_success("")
        except Exception as e:
            log_warning(f"  Error fetching articles: {e}")

    if article_ids:
        log_success_newline()
    return article_ids


async def create_article_views_async(
    token: str,
    article_ids: list[int],
    user_ids: dict[str, int],
) -> None:
    """
    Create article views to simulate users reading knowledge base articles.

    Views are recorded through the articles API with custom timestamps to
    simulate historical data over ~1 month period.
    """
    log_step("Creating article views with time distribution (async)")

    try:
        article_views = load_json("user_article_views.json")
    except FileNotFoundError:
        log_warning("  user_article_views.json not found, skipping article views")
        return

    total_views = 0
    view_payloads: list[dict[str, Any]] = []

    for view_data in article_views:
        user_key = view_data.get("user_key")
        article_indices = view_data.get("article_indices", [])
        view_counts = view_data.get("view_counts", [])
        days_ago = view_data.get("days_ago", 0)

        if user_key not in user_ids:
            continue

        user_id = user_ids[user_key]

        for i, article_idx in enumerate(article_indices):
            if article_idx >= len(article_ids):
                continue

            article_id = article_ids[article_idx]
            view_count = view_counts[i] if i < len(view_counts) else 1

            # Create multiple views with slight time variation
            for view_num in range(view_count):
                # Add slight variation in time for multiple views of same article
                hours_offset = view_num * 2  # 2 hours between views of same article
                view_time = (datetime.now() - timedelta(days=days_ago, hours=hours_offset)).isoformat()

                view_payloads.append(
                    {
                        "article_id": article_id,
                        "user_id": user_id,
                        "viewed_at": view_time,
                    }
                )
                total_views += 1

    if view_payloads:
        headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
        created_count = 0
        semaphore = asyncio.Semaphore(20)

        async def record_view(client: httpx.AsyncClient, view_payload: dict[str, Any]) -> None:
            nonlocal created_count
            async with semaphore:
                article_id = view_payload.pop("article_id")
                try:
                    response = await client.post(
                        f"{ADMIN_WEB_URL}/api/v1/articles/{article_id}/views",
                        headers=headers,
                        json=view_payload,
                    )
                    if response.status_code in (200, 201):
                        created_count += 1
                        log_success("")
                    else:
                        log_warning(
                            f"  Failed to record article view for article {article_id}: "
                            f"{response.status_code} - {response.text[:200]}"
                        )
                except Exception as e:
                    log_warning(f"  Error recording article view for article {article_id}: {e}")

        async with httpx.AsyncClient(follow_redirects=True, timeout=15.0) as client:
            await asyncio.gather(*(record_view(client, view_payload.copy()) for view_payload in view_payloads))
        if created_count == total_views:
            log_info(f"  Successfully recorded {created_count} article views with time distribution")
        else:
            log_warning(f"  Recorded {created_count}/{total_views} article views")
    else:
        log_warning("  No article views to insert")

    log_success_newline()


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
        (
            "Onboarding_Checklist.docx",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            51200,
            "Printable checklist version",
        ),
        ("Team_Structure.png", "image/png", 184320, "Org chart diagram"),
        ("Benefits_Overview.pdf", "application/pdf", 153600, "Health insurance and benefits guide"),
        ("Office_Map.jpg", "image/jpeg", 102400, "Office floor plan"),
        ("IT_Setup_Guide.pdf", "application/pdf", 307200, "Technical setup instructions"),
        ("Security_Policy.pdf", "application/pdf", 204800, "Information security guidelines"),
        (
            "Vacation_Request_Form.docx",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            25600,
            "Template for vacation requests",
        ),
        ("Code_Style_Guide.md", "text/markdown", 15360, "Development standards"),
        (
            "Project_Template.xlsx",
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            45056,
            "Project tracking spreadsheet",
        ),
        ("Emergency_Contacts.pdf", "application/pdf", 40960, "Important phone numbers"),
        ("Training_Schedule.ics", "text/calendar", 5120, "Onboarding events calendar"),
        ("Logo_Assets.zip", "application/zip", 512000, "Company logos and brand assets"),
        ("Remote_Access_Guide.pdf", "application/pdf", 176128, "VPN and remote work setup"),
        (
            "Expense_Report_Template.xlsx",
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            34816,
            "Expense submission template",
        ),
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
        file_selection = mock_files[idx % len(mock_files) : (idx % len(mock_files)) + num_files]
        if len(file_selection) < num_files:
            file_selection = mock_files[:num_files]

        for i, (filename, content_type, file_size, description) in enumerate(file_selection):
            # Generate varied synthetic file content
            content = generate_mock_file_content(filename, content_type, file_size, article_id, i)
            upload_tasks.append((article_id, filename, content, content_type, description, i))

    total_uploads = len(upload_tasks)
    success_count = 0

    async with httpx.AsyncClient(follow_redirects=True) as client:

        async def upload_file(
            article_id: int, filename: str, content: bytes, content_type: str, description: str, order: int
        ) -> None:
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
                    log_success("")
                else:
                    log_warning(f"  Failed to upload {filename}: {response.status_code} - {response.text}")
            except Exception as e:
                log_warning(f"  Error uploading {filename}: {e}")

        await asyncio.gather(
            *[
                upload_file(article_id, filename, content, content_type, description, i)
                for article_id, filename, content, content_type, description, i in upload_tasks
            ]
        )


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
        (
            "reference_letter.docx",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            30720,
            "Recommendation letter",
        ),
        ("medical_certificate.pdf", "application/pdf", 51200, "Health clearance"),
        ("training_completion.pdf", "application/pdf", 71680, "Course completion proof"),
        ("code_sample.py", "text/x-python", 8192, "Programming example"),
        (
            "project_presentation.pptx",
            "application/vnd.openxmlformats-officedocument.presentationml.presentation",
            153600,
            "Project deck",
        ),
        ("screenshot_proof.png", "image/png", 122880, "Completion screenshot"),
        ("setup_confirmation.txt", "text/plain", 1024, "Setup verification"),
        ("payroll_form.xls", "application/vnd.ms-excel", 22528, "Payroll information form"),
        ("contract.doc", "application/msword", 40960, "Employment contract"),
        (
            "benefits_form.xlsx",
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            18432,
            "Benefits enrollment",
        ),
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
            except Exception:
                return (checklist, [])
            else:
                return (checklist, [])

        checklist_task_pairs = await asyncio.gather(
            *[fetch_checklist_tasks(checklist) for checklist in checklists[:12]]
        )

        # Build list of upload tasks
        upload_tasks = []
        for checklist_idx, (checklist, tasks) in enumerate(checklist_task_pairs):
            if not tasks:
                continue
            checklist["id"]

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
                    log_success("")
                else:
                    log_warning(
                        f"  Failed to upload {filename} to task {task_id}: {response.status_code} - {response.text}"
                    )
            except Exception as e:
                log_warning(f"  Error uploading {filename} to task {task_id}: {e}")

        await asyncio.gather(
            *[
                upload_file(task_id, filename, content, content_type, description)
                for task_id, filename, content, content_type, description in upload_tasks
            ]
        )


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
                    log_success("")
                else:
                    log_warning(
                        f"  Failed to create scenario '{scenario_title}': {response.status_code} - {response.text}"
                    )
            except Exception as e:
                log_warning(f"  Error creating scenario '{scenario_title}': {e}")

        # Create scenarios with small delay between each to avoid overwhelming the DB
        created_count = 0
        for scenario in scenario_data:
            await create_scenario(scenario)
            created_count += 1
            await asyncio.sleep(0.1)  # Small delay between requests

    if created_count > 0:
        log_success_newline()


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
                    log_success("")
                    return meet_id
                log_warning(
                    f"  Failed to create meeting '{meeting['title']}': {response.status_code} - {response.text}"
                )
            except Exception as e:
                log_warning(f"  Error creating meeting '{meeting['title']}': {e}")
            return None

        # Create meetings with small delay between each to avoid overwhelming the DB
        meeting_ids = []
        for meet in meeting_data:
            meet_id = await create_meeting(meet)
            if meet_id is not None:
                meeting_ids.append(meet_id)
            await asyncio.sleep(0.1)  # Small delay between requests

    if meeting_ids:
        log_success_newline()
    return meeting_ids


async def fetch_existing_meeting_templates(
    token: str,
    dept_ids: dict[str, int],
    meeting_data: list[dict],
) -> list[int]:
    """Fetch existing meeting templates."""
    log_step("Fetching existing meeting templates")
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    meeting_ids: list[int] = []

    async with httpx.AsyncClient(follow_redirects=True) as client:
        for meeting in meeting_data:
            try:
                response = await client.get(
                    f"{ADMIN_WEB_URL}/api/v1/meetings/",
                    headers=headers,
                    params={"search": meeting["title"]},
                )
                if response.status_code == 200:
                    meetings = response.json()
                    if meetings:
                        meeting_id = meetings[0]["id"]
                        meeting_ids.append(meeting_id)
                        log_success("")
            except Exception as e:
                log_warning(f"  Error fetching meeting '{meeting['title']}': {e}")
            await asyncio.sleep(0.05)

    if meeting_ids:
        log_success_newline()
    return meeting_ids


async def create_user_meetings_async(
    token: str,
    meeting_template_ids: list[int],
    user_ids: dict[str, int],
) -> None:
    """Create all user meetings asynchronously."""
    log_step("Creating user meetings (async)")

    user_meetings_data = load_json("user_meetings.json")
    created_count = 0

    async def create_single_meeting(meeting: dict) -> None:
        nonlocal created_count
        user_key = meeting.get("user_key")
        status = meeting.get("status")
        days_ago = meeting.get("days_ago", 0)
        duration_minutes = meeting.get("duration_minutes")

        if user_key in user_ids:
            await create_user_meetings(
                token,
                meeting_template_ids,
                user_ids[user_key],
                days_ago,
                status,
                duration_minutes,
            )
            created_count += 1

    await asyncio.gather(*[create_single_meeting(m) for m in user_meetings_data])
    if created_count > 0:
        log_success_newline()


async def create_user_meetings(
    token: str,
    meeting_template_ids: list[int],
    user_id: int,
    scheduled_days_ago: int = 0,
    status: str = "SCHEDULED",
    duration_minutes: int | None = None,
) -> None:
    """Create user meeting instances."""
    if not meeting_template_ids:
        return

    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    # Use only first 3 templates per user to avoid duplicates
    templates_to_assign = meeting_template_ids[:3]

    async with httpx.AsyncClient(timeout=60.0, follow_redirects=True) as client:
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
                    log_success("")

                    if status in ["COMPLETED", "MISSED", "CANCELLED"]:
                        await client.patch(
                            f"{ADMIN_WEB_URL}/api/v1/user-meetings/{user_meeting_id}",
                            headers=headers,
                            json={"status": status},
                        )
                elif response.status_code in (400, 409):
                    # Meeting already assigned - skip silently
                    pass
                else:
                    log_warning(f"  Failed to create user meeting: {response.status_code} - {response.text[:200]}")

            except Exception as e:
                log_warning(f"  Error creating user meeting: {type(e).__name__}: {str(e)[:200]}")


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
                    log_success("")
                else:
                    log_warning(
                        f"  Failed to send notification to user {user_id}: {response.status_code} {response.text[:200]}"
                    )
            except Exception as e:
                log_warning(f"  Error sending notification: {e}")

        tasks = [send_notification(notif, user_id) for notif in notification_data for user_id in user_ids[:3]]

        await asyncio.gather(*tasks)
        if tasks:
            log_success_newline()


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

            days_ago = esc.get("days_ago", 0)
            created_at = (datetime.now() - timedelta(days=days_ago)).isoformat()
            esc_payload = {
                "user_id": user_id,
                "type": esc.get("type", "GENERAL"),
                "source": esc.get("source", "MANUAL"),
                "reason": esc.get("reason"),
                "context": esc.get("context", {}),
                "related_entity_type": esc.get("related_entity_type"),
                "related_entity_id": esc.get("related_entity_id"),
                "created_at": created_at,
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

                    log_success("")
                else:
                    log_warning(f"  Failed to create escalation: {response.status_code} - {response.text[:200]}")
            except Exception as e:
                log_warning(f"  Error creating escalation: {e}")

        tasks = [create_single_escalation(esc, i) for i, esc in enumerate(escalation_data)]
        results = await asyncio.gather(*tasks)
        if results:
            log_success_newline()


async def create_feedback_async(
    token: str,
    user_ids: dict[str, int],
    feedback_data: dict,
) -> None:
    """Create all feedback asynchronously."""
    log_step("Creating feedback (async)")
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
                    log_success("")
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
                    log_success("")
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
                    log_success("")
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

        total_created = len(pulse_data) + len(exp_data) + len(comment_data)
        for comment in comment_data:
            await create_comment(comment)
            await asyncio.sleep(0.05)

    if total_created > 0:
        log_success_newline()


async def create_pending_invitations_async(
    token: str,
    dept_ids: dict[str, int],
    mentor_id: int | None = None,
) -> None:
    """Create invitations asynchronously with various statuses (PENDING, USED, EXPIRED, REVOKED)."""
    log_step("Creating invitations (async)")
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    invitations = load_json("pending_invitations.json")

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
                    status = inv.get("status", "PENDING")
                    inv_id = inv_data.get("id")

                    # Update status if not default PENDING
                    if status != "PENDING" and inv_id:
                        await client.patch(
                            f"{ADMIN_WEB_URL}/api/v1/invitations/{inv_id}",
                            headers=headers,
                            json={"status": status},
                        )

                    log_success("")
                else:
                    log_warning(f"  Failed to create invitation: {response.status_code} - {response.text}")
            except Exception as e:
                log_warning(f"  Error creating invitation: {e}")

        await asyncio.gather(*[create_invitation(inv) for inv in invitations])
        log_success_newline()


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
                    log_success("")
                else:
                    log_warning(
                        f"  Failed to assign mentor {mentor_key} to {user_key}: {response.status_code} - {response.text}"
                    )
            except Exception as e:
                log_warning(f"  Error assigning mentor {mentor_key} to {user_key}: {e}")

        await asyncio.gather(*[create_relation(rel) for rel in user_mentors_data])
        log_success_newline()


async def create_search_queries_async(
    token: str,
    user_ids: dict[str, int],
) -> None:
    """Create search query records to simulate user search activity."""
    log_step("Creating search queries (async)")
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    try:
        search_queries = load_json("search_queries.json")
    except FileNotFoundError:
        log_warning("  search_queries.json not found, skipping search queries")
        return

    async with httpx.AsyncClient(follow_redirects=True) as client:

        async def create_query(query_data: dict) -> None:
            user_key = query_data.get("user_key")
            if user_key not in user_ids:
                return

            # Use the correct SearchQuery schema format
            # The user_id is extracted from the auth token automatically
            payload = {
                "query": query_data["query"],
                "page": 1,
                "size": 10,
            }

            # Simulate timing by adding delay based on days_ago
            # More recent queries (lower days_ago) get less delay
            days_ago = query_data.get("days_ago", 0)
            if days_ago > 0:
                delay = min(days_ago * 0.01, 1.0)  # Max 1 second delay
                await asyncio.sleep(delay)

            try:
                response = await client.post(
                    f"{ADMIN_WEB_URL}/api/v1/search",
                    headers=headers,
                    json=payload,
                )
                if response.status_code in (200, 201):
                    log_success("")
                else:
                    log_warning(f"  Search failed with status {response.status_code}: {response.text[:100]}")
            except Exception as e:
                log_warning(f"  Search request failed: {e}")

        await asyncio.gather(*[create_query(q) for q in search_queries[:100]])  # Limit to avoid overwhelming
        log_success_newline()


async def create_user_sessions_async(
    token: str,
    user_ids: dict[str, int],
    users_data: dict,
) -> None:
    """Create login/logout history by exercising the normal auth endpoints."""
    log_step("Creating user login/logout activity (async)")

    try:
        user_sessions = load_json("user_sessions.json")
    except FileNotFoundError:
        log_warning("  user_sessions.json not found, skipping user sessions")
        return

    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    created_count = 0

    async with httpx.AsyncClient(follow_redirects=True) as client:

        async def create_session(session_data: dict) -> None:
            nonlocal created_count
            user_key = session_data.get("user_key")
            user_data = users_data.get(user_key)
            if user_key not in user_ids or not user_data:
                log_warning(f"  Skipping login activity: user '{user_key}' not found")
                return

            login_token = await login_user(user_data["email"], user_data["password"])
            if not login_token:
                return

            created_count += 1
            log_success("")

            logout_resp = await client.post(
                f"{ADMIN_WEB_URL}/api/v1/auth/logout",
                headers={**headers, "Authorization": f"Bearer {login_token}"},
            )
            if logout_resp.status_code in (200, 201):
                log_success("")
            else:
                log_warning(f"  Failed to log out '{user_data['email']}': {logout_resp.status_code}")

        semaphore = asyncio.Semaphore(5)

        async def create_with_semaphore(session_data: dict) -> None:
            async with semaphore:
                await create_session(session_data)

        await asyncio.gather(*[create_with_semaphore(session_data) for session_data in user_sessions])

    if created_count > 0:
        log_success_newline()


async def fetch_existing_checklist_templates(token: str) -> list[int]:
    """Fetch existing checklist template IDs for selective audit-data generation."""
    log_step("Fetching existing checklist templates")
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    async with httpx.AsyncClient(follow_redirects=True) as client:
        try:
            response = await client.get(
                f"{ADMIN_WEB_URL}/api/v1/templates/",
                headers=headers,
                params={"limit": 100},
            )
            if response.status_code == 200:
                templates = response.json()
                template_ids = [template["id"] for template in templates if template.get("id")]
                if template_ids:
                    log_success_newline()
                return template_ids
            log_warning(f"  Failed to fetch checklist templates: {response.status_code} - {response.text[:200]}")
        except Exception as e:
            log_warning(f"  Error fetching checklist templates: {e}")

    return []


async def create_overdue_checklists_async(
    token: str,
    template_ids: list[int],
    users_data: dict,
    user_ids: dict[str, int],
    mentor_id: int | None,
    hr_id: int | None,
) -> None:
    """Create overdue checklist instances."""
    log_step("Creating overdue checklists (async)")

    try:
        overdue_checklists = load_json("overdue_checklists.json")
    except FileNotFoundError:
        log_warning("  overdue_checklists.json not found, skipping")
        return

    semaphore = asyncio.Semaphore(MOCK_DATA_CHECKLIST_CONCURRENCY)

    async def create_single_instance(instance: dict) -> None:
        async with semaphore:
            newbie_key = instance.get("user_key")
            status = instance.get("status")
            days_ago = instance.get("start_days_ago", 0)
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

    await asyncio.gather(*[create_single_instance(inst) for inst in overdue_checklists])
    log_success_newline()


async def create_deactivated_dialogs_async(
    token: str,
) -> None:
    """Create deactivated dialogue scenarios."""
    log_step("Creating deactivated dialogues (async)")
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    try:
        deactivated_dialogs = load_json("deactivated_dialogs.json")
    except FileNotFoundError:
        log_warning("  deactivated_dialogs.json not found, skipping")
        return

    async with httpx.AsyncClient(follow_redirects=True) as client:

        async def create_dialog(dialog: dict) -> None:
            dialog_payload = {
                "title": dialog["title"],
                "description": dialog.get("description"),
                "category": dialog.get("category"),
                "display_order": dialog.get("display_order"),
                "status": dialog.get("status", "INACTIVE"),
            }

            try:
                response = await client.post(
                    f"{ADMIN_WEB_URL}/api/v1/dialogue-scenarios/",
                    headers=headers,
                    json=dialog_payload,
                )
                if response.status_code in (200, 201):
                    log_success("")
                else:
                    log_warning(f"  Failed to create dialogue: {response.status_code}")
            except Exception as e:
                log_warning(f"  Error creating dialogue: {e}")

        await asyncio.gather(*[create_dialog(d) for d in deactivated_dialogs])
    log_success_newline()


async def create_requests_resolved_closed_async(
    token: str,
    user_ids: dict[str, int],
    hr_ids: list[int],
    mentor_ids: list[int],
) -> None:
    """Create requests with resolved and closed statuses."""
    log_step("Creating resolved/closed requests (async)")

    try:
        requests_data = load_json("requests_resolved_closed.json")
    except FileNotFoundError:
        log_warning("  requests_resolved_closed.json not found, skipping")
        return

    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    async with httpx.AsyncClient(follow_redirects=True) as client:

        async def create_request(request_data: dict) -> None:
            user_key = request_data.get("user_key")
            if user_key not in user_ids:
                log_warning(f"  User '{user_key}' not found, skipping request")
                return

            user_id = user_ids[user_key]
            created_days_ago = request_data.get("created_days_ago", 0)
            created_at = datetime.now() - timedelta(days=created_days_ago)

            # Create escalation request
            escalation_payload = {
                "user_id": user_id,
                "type": "GENERAL",
                "source": "MANUAL",
                "reason": request_data.get("subject"),
                "context": {"description": request_data.get("description")},
            }

            try:
                response = await client.post(
                    f"{ADMIN_WEB_URL}/api/v1/escalations/",
                    headers=headers,
                    json=escalation_payload,
                )

                if response.status_code in (200, 201):
                    escalation = response.json()
                    escalation_id = escalation["id"]
                    status = request_data.get("status", "PENDING")

                    # Update status if not PENDING
                    if status in ["RESOLVED", "CLOSED"]:
                        # First assign to an HR user
                        assignee_id = hr_ids[0] if hr_ids else mentor_ids[0] if mentor_ids else None
                        if assignee_id:
                            assign_resp = await client.post(
                                f"{ADMIN_WEB_URL}/api/v1/escalations/{escalation_id}/assign/{assignee_id}",
                                headers=headers,
                            )
                            if assign_resp.status_code in (200, 201):
                                # Set to IN_PROGRESS first
                                progress_resp = await client.patch(
                                    f"{ADMIN_WEB_URL}/api/v1/escalations/{escalation_id}",
                                    headers=headers,
                                    json={"status": "IN_PROGRESS"},
                                )
                                if progress_resp.status_code in (200, 201):
                                    # Resolve using the resolve endpoint
                                    update_resp = await client.post(
                                        f"{ADMIN_WEB_URL}/api/v1/escalations/{escalation_id}/resolve",
                                        headers=headers,
                                    )
                                    if update_resp.status_code in (200, 201):
                                        log_success("")
                                    else:
                                        log_warning(
                                            f"  Failed to resolve escalation: {update_resp.status_code} - {update_resp.text[:100]}"
                                        )
                                else:
                                    log_warning(f"  Failed to set IN_PROGRESS: {progress_resp.status_code}")
                            else:
                                log_warning(f"  Failed to assign escalation: {assign_resp.status_code}")
                        else:
                            log_warning("  No HR or mentor available to assign escalation")
                    else:
                        log_success("")
                else:
                    log_warning(f"  Failed to create escalation: {response.status_code}")
            except Exception as e:
                import traceback

                log_warning(f"  Error creating escalation: {e}")
                log_warning(f"  Traceback: {traceback.format_exc()[:500]}")

        # Limit concurrency to avoid connection pool exhaustion
        semaphore = asyncio.Semaphore(5)

        async def create_with_semaphore(req):
            async with semaphore:
                return await create_request(req)

        await asyncio.gather(*[create_with_semaphore(req) for req in requests_data])
    log_success_newline()


async def create_history_changes_async(
    token: str,
    user_ids: dict[str, int],
    users_data: dict,
    template_ids: list[int],
) -> None:
    """Create audit history by performing normal updates through service APIs."""
    log_step("Creating audit-history source changes (async)")

    try:
        load_json("history_changes.json")
    except FileNotFoundError:
        log_warning("  history_changes.json not found, skipping")
        return

    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    changed_count = 0
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if not template_ids:
        template_ids = await fetch_existing_checklist_templates(token)

    async with httpx.AsyncClient(follow_redirects=True) as client:
        for template_id in template_ids[:3]:
            try:
                response = await client.get(
                    f"{ADMIN_WEB_URL}/api/v1/templates/{template_id}",
                    headers=headers,
                )
                if response.status_code != 200:
                    log_warning(f"  Failed to fetch template {template_id}: {response.status_code}")
                    continue

                template = response.json()
                description = template.get("description") or ""
                update_resp = await client.put(
                    f"{ADMIN_WEB_URL}/api/v1/templates/{template_id}",
                    headers=headers,
                    json={
                        "description": f"{description}\nMock audit update at {timestamp}",
                    },
                )
                if update_resp.status_code in (200, 201):
                    changed_count += 1
                    log_success("")
                else:
                    log_warning(f"  Failed to update template {template_id}: {update_resp.status_code}")
            except Exception as e:
                log_warning(f"  Error updating template {template_id}: {e}")

        role_targets = [
            (user_key, user_id, users_data.get(user_key))
            for user_key, user_id in user_ids.items()
            if users_data.get(user_key, {}).get("role") == "NEWBIE"
        ]
        if role_targets:
            user_key, user_id, user_data = role_targets[0]
            original_role = user_data.get("role", "NEWBIE")
            try:
                promote_resp = await client.post(
                    f"{ADMIN_WEB_URL}/api/v1/users/{user_id}/change-role",
                    headers=headers,
                    params={"role": "MENTOR"},
                )
                restore_resp = await client.post(
                    f"{ADMIN_WEB_URL}/api/v1/users/{user_id}/change-role",
                    headers=headers,
                    params={"role": original_role},
                )
                if promote_resp.status_code in (200, 201) and restore_resp.status_code in (200, 201):
                    changed_count += 2
                    log_success("")
                    log_success("")
                else:
                    log_warning(
                        f"  Failed to create role-change history for {user_key}: "
                        f"{promote_resp.status_code}/{restore_resp.status_code}"
                    )
            except Exception as e:
                log_warning(f"  Error creating role-change history for {user_key}: {e}")

    if changed_count > 0:
        log_success_newline()


async def create_notification_templates_async(token: str) -> int:
    """Create notification templates for email and telegram channels. Returns count of created templates."""
    log_step("Creating notification templates (async)")

    try:
        templates_data = load_json("notification_templates.json")
    except FileNotFoundError:
        log_warning("  notification_templates.json not found, skipping")
        return 0

    headers = {"Authorization": f"Bearer {token}"}
    async with httpx.AsyncClient(timeout=60.0) as client:
        created_count = 0
        skipped_count = 0
        for template in templates_data:
            try:
                response = await client.post(
                    f"{ADMIN_WEB_URL}/api/v1/notification-templates/create",
                    headers=headers,
                    json=template,
                )
                if response.status_code in (200, 201):
                    created_count += 1
                    log_success("")
                elif response.status_code == 409:
                    # Template already exists - skip silently
                    skipped_count += 1
                else:
                    log_warning(
                        f"  Failed to create template '{template['name']}': {response.status_code} - {response.text}"
                    )
            except Exception as e:
                log_warning(f"  Error creating template '{template['name']}': {e}")

    if skipped_count > 0:
        pass
    else:
        pass

    return created_count


# Modular Data Generator Registry for scalability
class DataGeneratorRegistry:
    """Registry for modular data generators to enable easy extension."""

    def __init__(self):
        self.generators: dict[str, callable] = {}

    def register(self, name: str, generator: callable) -> None:
        """Register a data generator with a name."""
        self.generators[name] = generator

    async def run_all(self, context: dict, skip_services: list[str] | None = None) -> None:
        """Run all registered generators that are not skipped."""
        skip_services = skip_services or []
        for name, generator in self.generators.items():
            if name in skip_services:
                log_info(f"  Skipping {name}")
                continue
            log_step(f"Running {name}")
            try:
                await generator(**context)
            except Exception as e:
                log_warning(f"  Error in {name}: {e}")


async def create_supplementary_data(
    token: str,
    user_ids: dict[str, int],
    dept_ids: dict[str, int],
    template_ids: list[int],
    meeting_template_ids: list[int],
    article_ids: list[int],
    users_data: dict,
    hr_id: int | None,
    hr_ids: list[int],
    mentor_ids: list[int],
    skip_services: list[str] | None = None,
    only_data_types: list[str] | None = None,
    should_run: Callable | None = None,
) -> dict[str, int]:
    """Orchestrate all supplementary data creation for easy extension."""
    if only_data_types and not should_run:
        should_run = lambda dt: dt in only_data_types
    elif not should_run:
        should_run = lambda dt: True

    log_divider()
    log_step("Creating supplementary mock data")
    log_divider()
    print()

    # Core supplementary data
    if should_run("search_queries"):
        await create_search_queries_async(token, user_ids)
        log_success_newline()

    if should_run("user_sessions"):
        await create_user_sessions_async(token, user_ids, users_data)
        log_success_newline()

    if should_run("requests_resolved_closed"):
        await create_requests_resolved_closed_async(token, user_ids, hr_ids, mentor_ids)
        log_success_newline()

    if should_run("history_changes"):
        await create_history_changes_async(token, user_ids, users_data, template_ids)
        log_success_newline()

    if should_run("notification_templates") and "notification" not in skip_services:
        notification_templates_created = await create_notification_templates_async(token)
        log_success_newline()
    else:
        notification_templates_created = 0

    # Service-dependent supplementary data
    if should_run("overdue_checklists") and "checklists" not in skip_services:
        print()
        await create_overdue_checklists_async(
            token,
            template_ids,
            users_data,
            user_ids,
            mentor_ids[0] if mentor_ids else None,
            hr_id,
        )
        log_success_newline()

    if should_run("deactivated_dialogs") and "knowledge" not in skip_services:
        await create_deactivated_dialogs_async(token)
        log_success_newline()

    log_info("Supplementary data creation completed")

    return {"notification_templates": notification_templates_created}


async def main(
    skip_services: list[str] | None = None,
    only_data_types: list[str] | None = None,
    dry_run: bool = False,
) -> None:
    """Run mock data setup across all services with optional dry-run mode."""
    skip_services = skip_services or []
    only_data_types = only_data_types or []

    def should_run(data_type: str) -> bool:
        """Check if a data type should be run based on only_data_types filter."""
        if not only_data_types:
            return True
        return data_type in only_data_types

    log_divider()
    log_step("Mock Data Setup for Mentor Bot - Rich Demo Data")
    log_divider()

    if only_data_types:
        log_info(f"Selective mode: only creating {only_data_types}")

    if dry_run:
        log_warning("Running in DRY-RUN mode - no data will be created")

    log_info(f"Routing all API calls through {ADMIN_WEB_URL}")

    if not await wait_for_admin_web(ADMIN_WEB_URL):
        log_error("admin_web is not available. Exiting.")
        sys.exit(1)

    if not await wait_for_auth_service():
        log_error("auth_service is not available. Exiting.")
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

    # Departments
    if should_run("departments") or any(
        should_run(dt)
        for dt in [
            "users",
            "invitations",
            "checklists",
            "meeting",
            "notification",
            "escalation",
            "feedback",
            "knowledge",
            "search_queries",
            "user_sessions",
            "overdue_checklists",
            "requests_resolved_closed",
            "history_changes",
        ]
    ):
        if should_run("departments"):
            dept_ids = await create_departments(token)
        else:
            # Fetch existing departments
            dept_ids = await fetch_existing_departments(token)
    else:
        dept_ids = {}

    # Users (required for most other data types)
    if should_run("users") or any(
        should_run(dt)
        for dt in [
            "invitations",
            "checklists",
            "meeting",
            "notification",
            "escalation",
            "feedback",
            "knowledge",
            "search_queries",
            "user_sessions",
            "overdue_checklists",
            "requests_resolved_closed",
            "history_changes",
        ]
    ):
        users_data = load_json("users.json")
        if should_run("users"):
            user_ids, mentor_ids, hr_ids = await create_all_users_async(token, dept_ids)
        else:
            # Fetch existing users only (don't create in selective mode)
            user_ids, mentor_ids, hr_ids = await fetch_existing_users(token, dept_ids, users_data)
            if not user_ids:
                log_warning("  No existing users found - operations requiring users will be skipped")
    else:
        users_data = {}
        user_ids = {}
        mentor_ids = []
        hr_ids = []

    # User-mentor relationships
    if should_run("user_mentors"):
        await create_user_mentors_async(token, user_ids)

    template_ids: list[int] = []
    if should_run("checklists") and "checklists" not in skip_services:
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
        log_success_newline()

    meeting_template_ids: list[int] = []
    if should_run("meetings") and "meeting" not in skip_services:
        meetings = load_json("meetings.json")
        meeting_template_ids = await create_meeting_templates(token, dept_ids, meetings)
        await create_user_meetings_async(token, meeting_template_ids, user_ids)
        log_success_newline()
    elif should_run("user_meetings"):
        # Fetch existing meeting templates if needed for user_meetings
        meetings = load_json("meetings.json")
        meeting_template_ids = await fetch_existing_meeting_templates(token, dept_ids, meetings)

    if should_run("notifications") and "notification" not in skip_services:
        notifications = load_json("notifications.json")
        await create_notifications_async(token, list(user_ids.values()), notifications)
        log_success_newline()

    if should_run("escalations") and "escalation" not in skip_services:
        escalations = load_json("escalations.json")
        await create_escalations_async(token, list(user_ids.values()), escalations)
        log_success_newline()

    if should_run("feedback") and "feedback" not in skip_services:
        feedback = load_json("feedback.json")
        await create_feedback_async(token, user_ids, feedback)
        log_success_newline()

    article_ids: list[int] = []
    if should_run("knowledge") and "knowledge" not in skip_services:
        categories = load_json("knowledge_categories.json")
        cat_ids = await create_knowledge_categories(token, dept_ids, categories)
        log_success_newline()

        tags = load_json("knowledge_tags.json")
        tag_ids = await create_knowledge_tags(token, tags)
        log_success_newline()

        articles = load_json("knowledge_articles.json")
        article_ids = await create_knowledge_articles(token, cat_ids, tag_ids, dept_ids, articles)
        log_success_newline()

        scenarios = load_json("dialogue_scenarios.json")
        await create_dialogue_scenarios(token, scenarios)
        log_success_newline()

        # Create article views for users
        await create_article_views_async(token, article_ids, user_ids)

        # Create mock file attachments for articles
        await create_mock_article_attachments(token, article_ids, user_ids)
        log_success_newline()
    elif should_run("search_queries"):
        # Fetch existing knowledge data if needed for search queries
        categories = load_json("knowledge_categories.json")
        cat_ids = await fetch_existing_categories(token, dept_ids, categories)

        tags = load_json("knowledge_tags.json")
        tag_ids = await fetch_existing_tags(token, tags)

        articles = load_json("knowledge_articles.json")
        article_ids = await fetch_existing_articles(token, cat_ids, tag_ids, dept_ids, articles)

    if should_run("invitations"):
        await create_pending_invitations_async(token, dept_ids, mentor_ids[0] if mentor_ids else None)
        log_success_newline()

    # Create supplementary data (modular and easily extensible)
    supplementary_counts: dict[str, int] = {}
    if any(
        should_run(dt)
        for dt in [
            "search_queries",
            "user_sessions",
            "overdue_checklists",
            "deactivated_dialogs",
            "requests_resolved_closed",
            "history_changes",
            "notification_templates",
        ]
    ):
        supplementary_counts = await create_supplementary_data(
            token=token,
            user_ids=user_ids,
            dept_ids=dept_ids,
            template_ids=template_ids,
            meeting_template_ids=meeting_template_ids,
            article_ids=article_ids,
            users_data=users_data,
            hr_id=hr_ids[0] if hr_ids else None,
            hr_ids=hr_ids,
            mentor_ids=mentor_ids,
            skip_services=skip_services,
            only_data_types=only_data_types,
            should_run=should_run,
        )

    log_divider()
    log_step("Mock data setup completed successfully!")
    log_divider()
    log_info("Summary:")
    if dept_ids:
        log_info(f"  Departments:      {len(dept_ids)}")
    if user_ids:
        log_info(f"  Users:             {len(user_ids)}")
        log_info("  - Admins:          1")
        log_info(f"  - HR:              {len(hr_ids)}")
        log_info(f"  - Mentors:         {len(mentor_ids)}")
        # Count newbies and employees from users_data
        newbie_count = sum(1 for u in users_data.values() if u.get("role") == "NEWBIE")
        employee_count = sum(1 for u in users_data.values() if u.get("role") == "EMPLOYEE")
        if newbie_count > 0:
            log_info(f"  - Newbies:         {newbie_count}")
        if employee_count > 0:
            log_info(f"  - Employees:       {employee_count}")
    if template_ids:
        try:
            checklist_instances = load_json("checklist_instances.json")
            templates = load_json("templates.json")
            log_info(f"  Templates:         {len(templates)}")
            log_info(f"  Checklist instances: {len(checklist_instances)} (diverse completion: 0%, 25%, 50%, 75%, 100%)")
            log_info("  Task attachments:  Various files (PDFs, docs, images, etc.)")
        except FileNotFoundError:
            pass
    # Check if knowledge data was actually created by checking article_ids
    if article_ids:
        try:
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
        except FileNotFoundError:
            pass
    if meeting_template_ids:
        log_info(f"  Meeting templates: {len(meeting_template_ids)}")
        log_info("  User meetings:     Created (various statuses)")
    if should_run("escalations") and "escalation" not in skip_services:
        try:
            escalations = load_json("escalations.json")
            log_info(f"  Escalations:       {len(escalations)} (PENDING, ASSIGNED, IN_PROGRESS, RESOLVED, REJECTED)")
        except FileNotFoundError:
            pass
    if should_run("feedback") and "feedback" not in skip_services:
        try:
            feedback = load_json("feedback.json")
            pulse_count = len(feedback.get("pulse_surveys", []))
            exp_count = len(feedback.get("experience_ratings", []))
            comment_count = len(feedback.get("comments", []))
            log_info(f"  Feedback entries:  {pulse_count} pulse, {exp_count} experience, {comment_count} comments")
        except FileNotFoundError:
            pass
    if (
        should_run("notification_templates")
        and "notification" not in skip_services
        and supplementary_counts.get("notification_templates", 0) > 0
    ):
        log_info(f"  Notification templates: {supplementary_counts['notification_templates']}")
    if should_run("invitations") and "checklists" not in skip_services:
        try:
            invitations = load_json("pending_invitations.json")
            log_info(f"  Invitations:       {len(invitations)}")
        except FileNotFoundError:
            pass
    if should_run("user_mentors") and user_ids:
        try:
            user_mentors = load_json("user_mentors.json")
            log_info(f"  User-Mentor relations: {len(user_mentors)}")
        except FileNotFoundError:
            pass
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
        "--only",
        type=str,
        default="",
        help="Comma-separated list of data types to create (e.g., 'departments,users,invitations,meetings,checklists,knowledge,notification,escalation,feedback,search_queries,user_sessions,overdue_checklists,deactivated_dialogs,requests_resolved_closed,history_changes,notification_templates')",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Run without actually creating data",
    )
    parser.add_argument(
        "--checklist-concurrency",
        type=int,
        default=None,
        help=(
            "Maximum concurrent checklist create/update flows "
            "(default: $MOCK_DATA_CHECKLIST_CONCURRENCY or 2)"
        ),
    )

    args = parser.parse_args()
    if args.admin_web_url:
        ADMIN_WEB_URL = args.admin_web_url.rstrip("/")
    if args.checklist_concurrency is not None:
        if args.checklist_concurrency < 1:
            parser.error("--checklist-concurrency must be a positive integer")
        MOCK_DATA_CHECKLIST_CONCURRENCY = args.checklist_concurrency
    skip_list = [s.strip() for s in args.skip_services.split(",") if s.strip()]
    only_list = [s.strip() for s in args.only.split(",") if s.strip()]

    asyncio.run(main(skip_services=skip_list, only_data_types=only_list, dry_run=args.dry_run))
