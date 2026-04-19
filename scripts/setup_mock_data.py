#!/usr/bin/env python3
"""
Mock Data Setup Script for Mentor Bot.

Creates test data across all microservices using JSON configuration files.
Generates rich data for demonstration purposes - various statuses, roles, etc.

Usage:
    python scripts/setup_mock_data.py [--skip-services=SERVICES] [--dry-run]
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


async def create_departments(token: str) -> dict[str, int]:
    """Create departments via auth service API (which syncs to other services automatically)."""
    log_step("Creating departments")
    departments = load_json("departments.json")
    dept_ids: dict[str, int] = {}
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    async with httpx.AsyncClient() as client:
        tasks = [_create_or_get_department(client, headers, dept) for dept in departments]
        results = await asyncio.gather(*tasks)

    for name, dept_id in results:
        if dept_id is not None:
            dept_ids[name] = dept_id

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
            f"{AUTH_SERVICE_URL}/api/v1/departments/",
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
            f"{AUTH_SERVICE_URL}/api/v1/departments/",
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
            f"{AUTH_SERVICE_URL}/api/v1/users/by-email/{user_data['email']}",
            headers=headers,
        )
        if response.status_code == 200:
            user_id = response.json()["id"]
            log_success(f"  User '{user_data['email']}' already exists (ID: {user_id})")
            return (user_data.get("key", ""), user_id)

        response = await client.post(
            f"{AUTH_SERVICE_URL}/api/v1/users/",
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

    async with httpx.AsyncClient(timeout=30.0) as client:
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

    async with httpx.AsyncClient() as client:
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
                f"{CHECKLISTS_SERVICE_URL}/api/v1/checklists/",
                headers=headers,
                json=checklist_data,
            )

            if response.status_code in (200, 201):
                checklist = response.json()
                checklist_id = checklist["id"]
                log_success(f"  Checklist {checklist_id} created for user {user_id} (status: {status}, template: {template_index})")

                if status == "COMPLETED" or completed_task_count > 0:
                    await update_checklist_tasks(client, headers, checklist_id, completed_task_count, status)

                if status == "COMPLETED":
                    # Use the complete endpoint to mark checklist as done
                    await client.post(
                        f"{CHECKLISTS_SERVICE_URL}/api/v1/checklists/{checklist_id}/complete",
                        headers=headers,
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
        # Correct endpoint for getting tasks by checklist
        response = await client.get(
            f"{CHECKLISTS_SERVICE_URL}/api/v1/tasks/checklist/{checklist_id}",
            headers=headers,
        )

        if response.status_code == 200:
            tasks = response.json() if isinstance(response.json(), list) else response.json().get("tasks", [])
            for i, task in enumerate(tasks):
                task_id = task["id"]
                if i < completed_count:
                    # Use complete endpoint for completed tasks, progress for in-progress
                    if status == "COMPLETED":
                        await client.post(
                            f"{CHECKLISTS_SERVICE_URL}/api/v1/tasks/{task_id}/complete",
                            headers=headers,
                        )
                    else:
                        await client.post(
                            f"{CHECKLISTS_SERVICE_URL}/api/v1/tasks/{task_id}/progress",
                            headers=headers,
                            json={"progress_percentage": min(100, (i + 1) * 100 // len(tasks))},
                        )
    except Exception as e:
        log_warning(f"  Error updating tasks: {e}")


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
    async with httpx.AsyncClient() as client:
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
                            f"{KNOWLEDGE_SERVICE_URL}/api/v1/articles/{article_id}",
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

    total_uploads = 0
    success_count = 0

    async with httpx.AsyncClient() as client:
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

                try:
                    response = await client.post(
                        f"{KNOWLEDGE_SERVICE_URL}/api/v1/attachments/upload",
                        headers=headers,
                        data={
                            "article_id": str(article_id),
                            "description": description,
                            "order": str(i),
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
                        log_warning(f"  Failed to upload {filename}: {response.status_code}")
                    total_uploads += 1
                except Exception as e:
                    log_warning(f"  Error uploading {filename}: {e}")
                    total_uploads += 1

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

    total_uploads = 0
    success_count = 0

    async with httpx.AsyncClient() as client:
        # First, get some checklists with tasks to attach files to
        try:
            response = await client.get(
                f"{CHECKLISTS_SERVICE_URL}/api/v1/checklists/",
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

        for checklist_idx, checklist in enumerate(checklists[:12]):  # Attach to ~12 checklists
            checklist_id = checklist["id"]

            # Get tasks for this checklist
            try:
                response = await client.get(
                    f"{CHECKLISTS_SERVICE_URL}/api/v1/tasks/checklist/{checklist_id}",
                    headers={**headers, "Content-Type": "application/json"},
                )
                if response.status_code != 200:
                    continue
                tasks = response.json()
            except Exception:
                continue

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

                try:
                    response = await client.post(
                        f"{CHECKLISTS_SERVICE_URL}/api/v1/tasks/{task_id}/attachments",
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
                        log_warning(f"  Failed to upload {filename} to task {task_id}: {response.status_code}")
                    total_uploads += 1
                except Exception as e:
                    log_warning(f"  Error uploading {filename} to task {task_id}: {e}")
                    total_uploads += 1

                # Occasionally add a second file (30% chance)
                if checklist_idx % 3 == 0 and task_idx == 0:
                    second_file_idx = (file_idx + 1) % len(task_files)
                    filename2, content_type2, file_size2, desc2 = task_files[second_file_idx]
                    content2 = generate_mock_file_content(filename2, content_type2, file_size2, task_id, task_idx + 10)

                    try:
                        response = await client.post(
                            f"{CHECKLISTS_SERVICE_URL}/api/v1/tasks/{task_id}/attachments",
                            headers=headers,
                            data={"description": desc2},
                            files={
                                "file": (filename2, content2, content_type2),
                            },
                            timeout=30.0,
                        )
                        if response.status_code in (200, 201):
                            success_count += 1
                            log_success(f"  Uploaded {filename2} to task {task_id}")
                        else:
                            log_warning(f"  Failed to upload {filename2}: {response.status_code}")
                        total_uploads += 1
                    except Exception as e:
                        log_warning(f"  Error uploading {filename2}: {e}")
                        total_uploads += 1

    log_success(f"  Created {success_count}/{total_uploads} task attachments")


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


async def create_meeting_templates(
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

    async with httpx.AsyncClient() as client:
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
                    f"{MEETING_SERVICE_URL}/api/v1/user-meetings/assign",
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
                            f"{MEETING_SERVICE_URL}/api/v1/user-meetings/{user_meeting_id}",
                            headers=headers,
                            json={"status": status},
                        )
                elif response.status_code == 409:
                    # Meeting already assigned - skip silently
                    pass
                else:
                    log_warning(f"  Failed to create user meeting: {response.status_code} {response.text[:200]}")

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

    async with httpx.AsyncClient() as client:

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
                    f"{NOTIFICATION_SERVICE_URL}/api/v1/notifications/send",
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

        tasks = []
        for notif in notification_data:
            for user_id in user_ids[:3]:
                tasks.append(send_notification(notif, user_id))

        await asyncio.gather(*tasks)


async def create_escalations_async(
    token: str,
    user_ids: list[int],
    escalation_data: list[dict],
) -> None:
    """Create all escalations asynchronously."""
    log_step("Creating escalations (async)")
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {token}"}

    async with httpx.AsyncClient() as client:

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
                    f"{ESCALATION_SERVICE_URL}/api/v1/escalations/",
                    headers=headers,
                    json=esc_payload,
                )
                if response.status_code in (200, 201):
                    escalation = response.json()
                    esc_id = escalation["id"]

                    status = esc.get("status", "PENDING")
                    if status != "PENDING":
                        await client.patch(
                            f"{ESCALATION_SERVICE_URL}/api/v1/escalations/{esc_id}",
                            headers=headers,
                            json={"status": status},
                        )

                    log_success(f"  Escalation {esc_id} created (status: {status})")
                else:
                    log_warning(f"  Failed to create escalation: {response.status_code} {response.text[:200]}")
            except Exception as e:
                log_warning(f"  Error creating escalation: {e}")

        tasks = [create_single_escalation(esc, i) for i, esc in enumerate(escalation_data)]
        await asyncio.gather(*tasks)


async def create_feedback_async(
    user_ids: list[int],
    feedback_data: dict,
) -> None:
    """Create all feedback asynchronously."""
    log_step("Creating feedback (async)")

    async with httpx.AsyncClient() as client:
        pulse_data = feedback_data.get("pulse_surveys", [])
        exp_data = feedback_data.get("experience_ratings", [])
        comment_data = feedback_data.get("comments", [])

        async def create_pulse(pulse: dict, idx: int) -> None:
            if idx >= len(user_ids):
                return
            payload = {"user_id": user_ids[idx], "rating": pulse.get("rating", 7)}
            try:
                response = await client.post(
                    f"{FEEDBACK_SERVICE_URL}/api/v1/feedback/pulse",
                    json=payload,
                )
                if response.status_code in (200, 201):
                    log_success(f"  Pulse survey created for user {user_ids[idx]} (rating: {payload['rating']})")
            except Exception as e:
                log_warning(f"  Error creating pulse survey: {e}")

        async def create_experience(exp: dict, idx: int) -> None:
            if idx >= len(user_ids):
                return
            payload = {"user_id": user_ids[idx], "rating": exp.get("rating", 4)}
            try:
                response = await client.post(
                    f"{FEEDBACK_SERVICE_URL}/api/v1/feedback/experience",
                    json=payload,
                )
                if response.status_code in (200, 201):
                    log_success(f"  Experience rating created for user {user_ids[idx]} (rating: {payload['rating']})")
            except Exception as e:
                log_warning(f"  Error creating experience rating: {e}")

        async def create_comment(comment: dict, idx: int) -> None:
            if idx >= len(user_ids):
                return
            payload = {"user_id": user_ids[idx], "comment": comment.get("comment", "Great experience!")}
            try:
                response = await client.post(
                    f"{FEEDBACK_SERVICE_URL}/api/v1/feedback/comments",
                    json=payload,
                )
                if response.status_code in (200, 201):
                    log_success(f"  Comment created for user {user_ids[idx]}")
            except Exception as e:
                log_warning(f"  Error creating comment: {e}")

        tasks = []
        tasks.extend([create_pulse(p, i) for i, p in enumerate(pulse_data[:5])])
        tasks.extend([create_experience(e, i) for i, e in enumerate(exp_data[:5])])
        tasks.extend([create_comment(c, i) for i, c in enumerate(comment_data[:5])])

        await asyncio.gather(*tasks)


async def create_pending_invitations_async(
    token: str,
    dept_ids: dict[str, int],
    mentor_id: int | None = None,
) -> None:
    """Create pending invitations asynchronously."""
    log_step("Creating pending invitations (async)")
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    pending_invitations = load_json("pending_invitations.json")

    async with httpx.AsyncClient() as client:

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

        await asyncio.gather(*[create_invitation(inv) for inv in pending_invitations])


async def create_user_mentors_async(
    token: str,
    user_ids: dict[str, int],
) -> None:
    """Create user-mentor relationships asynchronously."""
    log_step("Creating user-mentor relationships (async)")
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    user_mentors_data = load_json("user_mentors.json")

    async with httpx.AsyncClient() as client:

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
                    f"{AUTH_SERVICE_URL}/api/v1/user-mentors/",
                    headers=headers,
                    json=payload,
                )
                if response.status_code in (200, 201):
                    log_success(f"  Mentor assigned: {user_key} -> {mentor_key}")
                else:
                    log_warning(f"  Failed to assign mentor {mentor_key} to {user_key}: {response.status_code}")
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

    if not dry_run and not create_admin_user():
        log_error("Failed to create admin user. Exiting.")
        sys.exit(1)

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
        await create_feedback_async(list(user_ids.values()), feedback)

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
        log_info("  Feedback entries: 15 (pulse, experience, comments)")
    user_mentors = load_json("user_mentors.json")
    log_info(f"  User-Mentor relations: {len(user_mentors)}")
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
