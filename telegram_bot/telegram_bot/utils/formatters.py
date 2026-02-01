"""Text formatting utilities."""

from datetime import UTC, datetime
from typing import Any

from aiogram.types import User as TgUser


def format_welcome_message(tg_user: TgUser, user_data: dict[str, Any] | None = None) -> str:
    """Format welcome message for user."""
    name = tg_user.first_name
    if tg_user.last_name:
        name += f" {tg_user.last_name}"

    if user_data:
        welcome = (
            f"👋 Welcome back, *{name}!*\n\n"
            f"🎯 *Employee ID:* {user_data.get('employee_id', 'N/A')}\n"
            f"🏢 *Department:* {user_data.get('department', 'N/A')}\n"
            f"👨‍💼 *Position:* {user_data.get('position', 'N/A')}\n\n"
            "I'm here to help you with your onboarding process. "
            "Use the menu below to get started!"
        )
    else:
        welcome = (
            f"👋 Welcome, *{name}!*\n\n"
            "I'm Mentor Bot, your personal onboarding assistant.\n\n"
            "I can help you with:\n"
            "• 📋 Onboarding checklist\n"
            "• 🔍 Knowledge base search\n"
            "• 👨‍🏫 Mentor communication\n"
            "• 📞 HR support\n\n"
            "Let's get started!"
        )

    return welcome


def format_checklist_progress(checklist: dict[str, Any]) -> str:
    """Format checklist progress for display."""
    name = checklist.get("name", f"Checklist #{checklist['id']}")
    progress = checklist.get("progress_percentage", 0)
    status = checklist.get("status", "unknown").lower()
    total = checklist.get("total_tasks", 0)
    completed = checklist.get("completed_tasks", 0)

    # Status emoji
    if status == "completed":
        status_emoji = "✅"
    elif status == "in_progress":
        status_emoji = "🔄"
    elif status == "overdue":
        status_emoji = "⚠️"
    else:
        status_emoji = "📋"

    # Progress bar
    bars = 10
    filled = int(progress / 100 * bars)
    bar = "█" * filled + "░" * (bars - filled)

    return f"{status_emoji} *{name}*\n`{bar}` {progress}%\n📊 {completed}/{total} tasks completed\n\n"


def format_task_list(tasks: list[dict[str, Any]]) -> str:
    """Format task list for display."""
    if not tasks:
        return "📭 No tasks found."

    text = "📋 *Tasks*\n\n"

    for i, task in enumerate(tasks[:10], 1):  # Show first 10 tasks
        title = task.get("title", f"Task #{task['id']}")
        status = task.get("status", "pending").lower()
        category = task.get("category", "general")

        # Status emoji
        if status == "completed":
            emoji = "✅"
        elif status == "in_progress":
            emoji = "🔄"
        elif status == "blocked":
            emoji = "⛔"
        elif status == "overdue":
            emoji = "⚠️"
        else:
            emoji = "📝"

        # Due date if available
        due_date = task.get("due_date")
        due_text = ""
        if due_date:
            try:
                due_dt = datetime.fromisoformat(due_date)
                due_text = f" | Due: {due_dt.strftime('%b %d')}"
            except:
                pass

        text += f"{i}. {emoji} *{title}*\n"
        text += f"   📁 {category}{due_text}\n\n"

    if len(tasks) > 10:
        text += f"... and {len(tasks) - 10} more tasks\n\n"

    return text


def format_task_detail(task: dict[str, Any]) -> str:
    """Format task details for display."""
    title = task.get("title", f"Task #{task['id']}")
    description = task.get("description", "No description provided.")
    status = task.get("status", "pending").lower()
    category = task.get("category", "general")

    # Status text
    status_text = {
        "pending": "⏳ Pending",
        "in_progress": "🔄 In Progress",
        "completed": "✅ Completed",
        "blocked": "⛔ Blocked",
        "overdue": "⚠️ Overdue",
    }.get(status, "❓ Unknown")

    text = f"📋 *{title}*\n\n"
    text += f"*Status:* {status_text}\n"
    text += f"*Category:* {category}\n"

    # Due date
    due_date = task.get("due_date")
    if due_date:
        try:
            due_dt = datetime.fromisoformat(due_date)
            text += f"*Due Date:* {due_dt.strftime('%B %d, %Y')}\n"

            # Check if overdue
            if status == "pending" and due_dt < datetime.now(UTC):
                text += "⚠️ *This task is overdue!*\n"
        except:
            pass

    # Description
    text += f"\n*Description:*\n{description}\n"

    # Dependencies
    dependencies = task.get("depends_on", [])
    if dependencies:
        text += f"\n*Depends on:* {len(dependencies)} task(s)\n"

    # Assignee
    assignee = task.get("assignee")
    if assignee:
        text += f"\n*Assigned to:* {assignee}\n"

    return text


def format_search_results(query: str, results: list[dict[str, Any]]) -> str:
    """Format search results for display."""
    if not results:
        return f"🔍 No results found for '*{query}*'"

    text = f"🔍 *Search Results for '{query}'*\n\n"

    for i, result in enumerate(results[:5], 1):
        title = result.get("title", "Untitled")
        snippet = result.get("snippet", "")
        category = result.get("category", "General")
        relevance = result.get("relevance", 0)

        rel_bar = "★" * int(relevance * 5) + "☆" * (5 - int(relevance * 5))

        text += f"{i}. *{title}*\n"
        text += f"   📁 {category} | {rel_bar}\n"
        text += f"   {snippet[:100]}...\n\n"

    if len(results) > 5:
        text += f"📄 *{len(results) - 5} more results not shown*\n"

    text += "\n*Select a result number or refine your search.*"

    return text


def format_date(dt: datetime) -> str:
    """Format datetime for display."""
    now = datetime.now(UTC)
    diff = now - dt

    if diff.days == 0:
        return "Today"
    if diff.days == 1:
        return "Yesterday"
    if diff.days < 7:
        return f"{diff.days} days ago"
    return dt.strftime("%b %d, %Y")


def format_percentage(value: float) -> str:
    """Format percentage value."""
    return f"{value:.1f}%"
