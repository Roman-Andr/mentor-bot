"""Text formatting utilities."""

from datetime import UTC, datetime
from typing import Any

from aiogram.types import User as TgUser

from telegram_bot.i18n import t

MAX_DISPLAYED_TASKS = 10
MAX_SEARCH_RESULTS_DISPLAY = 5
DAYS_THRESHOLD_OLD = 7
MAX_DISPLAYED_MEETINGS = 5
MAX_DISPLAYED_ESCALATIONS = 5


def format_welcome_message(
    tg_user: TgUser, user_data: dict[str, Any] | None = None, *, locale: str = "en"
) -> str:
    """Format welcome message for user."""
    name = tg_user.first_name or ""
    if tg_user.last_name:
        name += f" {tg_user.last_name}"

    if user_data:
        eid = user_data.get("employee_id", "N/A")
        dept = user_data.get("department", "N/A")
        pos = user_data.get("position", "N/A")
        welcome = "\U0001f44b " + t(
            "start.welcome_back",
            locale=locale,
            name=name,
            employee_id=eid,
            department=dept,
            position=pos,
        )
    else:
        welcome = t("start.welcome_new", locale=locale)

    return welcome


def format_checklist_progress(checklist: dict[str, Any], *, locale: str = "en") -> str:
    """Format checklist progress for display."""
    name = checklist.get("name", f"Checklist #{checklist['id']}")
    progress = checklist.get("progress_percentage", 0)
    status = checklist.get("status", "unknown").lower()
    total = checklist.get("total_tasks", 0)
    completed = checklist.get("completed_tasks", 0)

    if status == "completed":
        status_emoji = "\u2705"
    elif status == "in_progress":
        status_emoji = "\U0001f504"
    elif status == "overdue":
        status_emoji = "\u26a0\ufe0f"
    else:
        status_emoji = "\U0001f4cb"

    bars = 10
    filled = int(progress / 100 * bars)
    bar = "\u2588" * filled + "\u2591" * (bars - filled)

    return f"{status_emoji} *{name}*\n`{bar}` {progress}%\n\U0001f4ca {completed}/{total} tasks completed\n\n"


def format_task_list(tasks: list[dict[str, Any]], *, locale: str = "en") -> str:
    """Format task list for display."""
    if not tasks:
        return t("checklists.no_tasks_general", locale=locale)

    text = f"\U0001f4cb *{t('checklists.tasks_title', locale=locale)}*\n\n"

    for i, task in enumerate(tasks[:MAX_DISPLAYED_TASKS], 1):
        title = task.get("title", f"Task #{task['id']}")
        status = task.get("status", "pending").lower()
        category = task.get("category", "general")

        if status == "completed":
            emoji = "\u2705"
        elif status == "in_progress":
            emoji = "\U0001f504"
        elif status == "blocked":
            emoji = "\u26d4"
        elif status == "overdue":
            emoji = "\u26a0\ufe0f"
        else:
            emoji = "\U0001f4dd"

        due_date = task.get("due_date")
        due_text = ""
        if due_date:
            try:
                due_dt = datetime.fromisoformat(due_date)
                due_text = f" | Due: {due_dt.strftime('%b %d')}"
            except ValueError:
                pass

        text += f"{i}. {emoji} *{title}*\n"
        text += f"   \U0001f4c1 {category}{due_text}\n\n"

    if len(tasks) > MAX_DISPLAYED_TASKS:
        text += f"... and {len(tasks) - MAX_DISPLAYED_TASKS} more tasks\n\n"

    return text


def format_task_detail(task: dict[str, Any], *, locale: str = "en") -> str:
    """Format task details for display."""
    title = task.get("title", f"Task #{task['id']}")
    description = task.get("description", "No description provided.")
    status = task.get("status", "pending").lower()
    category = task.get("category", "general")

    status_text = {
        "pending": "\u23f3 Pending",
        "in_progress": "\U0001f504 In Progress",
        "completed": "\u2705 Completed",
        "blocked": "\u26d4 Blocked",
        "overdue": "\u26a0\ufe0f Overdue",
    }.get(status, "\u2753 Unknown")

    text = f"\U0001f4cb *{title}*\n\n"
    text += f"*Status:* {status_text}\n"
    text += f"*Category:* {category}\n"

    due_date = task.get("due_date")
    if due_date:
        try:
            due_dt = datetime.fromisoformat(due_date)
            text += f"*Due Date:* {due_dt.strftime('%B %d, %Y')}\n"

            if status == "pending" and due_dt < datetime.now(UTC):
                text += "\u26a0\ufe0f *This task is overdue!*\n"
        except ValueError:
            pass

    text += f"\n*Description:*\n{description}\n"

    dependencies = task.get("depends_on", [])
    if dependencies:
        text += f"\n*Depends on:* {len(dependencies)} task(s)\n"

    assignee = task.get("assignee")
    if assignee:
        text += f"\n*Assigned to:* {assignee}\n"

    return text


def format_search_results(
    query: str, results: list[dict[str, Any]], *, locale: str = "en"
) -> str:
    """Format search results for display."""
    if not results:
        return f"\U0001f50d No results found for '*{query}*'"

    text = f"\U0001f50d *{t('knowledge.search_results_title', locale=locale, query=query)}*\n\n"

    for i, result in enumerate(results[:MAX_SEARCH_RESULTS_DISPLAY], 1):
        title = result.get("title", "Untitled")
        snippet = result.get("snippet", "")
        category = result.get("category", "General")
        relevance = result.get("relevance", 0)

        rel_bar = "\u2605" * int(relevance * 5) + "\u2606" * (5 - int(relevance * 5))

        text += f"{i}. *{title}*\n"
        text += f"   \U0001f4c1 {category} | {rel_bar}\n"
        text += f"   {snippet[:100]}...\n\n"

    if len(results) > MAX_SEARCH_RESULTS_DISPLAY:
        text += f"\U0001f4c4 *{len(results) - MAX_SEARCH_RESULTS_DISPLAY} more results not shown*\n"

    return text


def format_date(dt: datetime) -> str:
    """Format datetime for display."""
    now = datetime.now(UTC)
    diff = now - dt

    if diff.days == 0:
        return "Today"
    if diff.days == 1:
        return "Yesterday"
    if diff.days < DAYS_THRESHOLD_OLD:
        return f"{diff.days} days ago"
    return dt.strftime("%b %d, %Y")


def format_percentage(value: float) -> str:
    """Format percentage value."""
    return f"{value:.1f}%"


def format_feedback_menu(*, locale: str = "en") -> str:
    """Format feedback menu for display."""
    return (
        f"*\U0001f4ca {t('feedback.title', locale=locale)}*\n\n"
        f"{t('feedback.description', locale=locale)}\n\n"
        f"*{t('feedback.options', locale=locale)}*\n"
        f"  \U0001f60a {t('feedback.opt_pulse', locale=locale)}\n"
        f"  \u2b50 {t('feedback.opt_experience', locale=locale)}\n"
        f"  \U0001f4ac {t('feedback.opt_comments', locale=locale)}\n\n"
        f"{t('feedback.anonymous', locale=locale)}"
    )


def format_meeting_list(meetings: list[dict[str, Any]], *, locale: str = "en") -> str:
    """Format meeting list for display."""
    if not meetings:
        return t("meetings.no_meetings_list", locale=locale)

    text = "\U0001f4c5 *Upcoming Meetings*\n\n"

    for i, meeting in enumerate(meetings[:MAX_DISPLAYED_MEETINGS], 1):
        title = meeting.get("title", f"Meeting #{meeting['id']}")
        scheduled_at = meeting.get("scheduled_at", "TBD")
        meeting_type = meeting.get("meeting_type", "general")

        try:
            dt = datetime.fromisoformat(scheduled_at)
            formatted_date = dt.strftime("%b %d, %Y %H:%M")
        except ValueError:
            formatted_date = scheduled_at

        type_emoji = {
            "onboarding": "\U0001f44b",
            "mentor": "\U0001f468\u200d\U0001f3eb",
            "hr": "\U0001f4de",
            "technical": "\U0001f4bb",
        }.get(meeting_type, "\U0001f4c5")

        text += f"{i}. {type_emoji} *{title}*\n"
        text += f"   \U0001f4c5 {formatted_date}\n\n"

    if len(meetings) > MAX_DISPLAYED_MEETINGS:
        text += f"... and {len(meetings) - MAX_DISPLAYED_MEETINGS} more meetings\n\n"

    return text


def format_escalation_list(
    escalations: list[dict[str, Any]], *, locale: str = "en"
) -> str:
    """Format escalation list for display."""
    if not escalations:
        return t("escalation.no_escalations", locale=locale)

    text = "\U0001f4de *Your Escalations*\n\n"

    for i, escalation in enumerate(escalations[:MAX_DISPLAYED_ESCALATIONS], 1):
        title = escalation.get("title", f"Escalation #{escalation['id']}")
        status = escalation.get("status", "open").lower()
        category = escalation.get("category", "General")
        created_at = escalation.get("created_at", "N/A")

        status_emoji = {
            "open": "\u23f3",
            "in_progress": "\U0001f504",
            "resolved": "\u2705",
            "closed": "\U0001f512",
        }.get(status, "\u2753")

        try:
            dt = datetime.fromisoformat(created_at)
            formatted_date = dt.strftime("%b %d")
        except ValueError:
            formatted_date = created_at

        text += f"{i}. {status_emoji} *{title}*\n"
        text += f"   \U0001f4c1 {category} | \U0001f4c5 {formatted_date}\n\n"

    if len(escalations) > MAX_DISPLAYED_ESCALATIONS:
        text += f"... and {len(escalations) - MAX_DISPLAYED_ESCALATIONS} more escalations\n\n"

    return text
