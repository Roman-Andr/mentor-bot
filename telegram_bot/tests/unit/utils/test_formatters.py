"""Unit tests for telegram_bot/utils/formatters.py."""

from datetime import UTC, datetime, timedelta

from telegram_bot.utils.formatters import (
    MAX_DISPLAYED_TASKS,
    format_checklist_progress,
    format_date,
    format_meeting_list,
    format_task_list,
    format_welcome_message,
)


class TestFormatWelcomeMessage:
    """Test cases for format_welcome_message function."""

    def test_with_user_data_and_dict_department(self, mock_tg_user):
        """Welcome message with user_data and department as dict."""
        user_data = {
            "employee_id": "EMP123",
            "department": {"name": "Engineering"},
            "position": "Developer",
        }
        result = format_welcome_message(mock_tg_user, user_data, locale="en")
        assert "John Doe" in result
        assert "EMP123" in result
        assert "Engineering" in result
        assert "Developer" in result

    def test_with_user_data_and_string_department(self, mock_tg_user):
        """Welcome message with user_data and department as string."""
        user_data = {
            "employee_id": "EMP456",
            "department": "Sales",
            "position": "Manager",
        }
        result = format_welcome_message(mock_tg_user, user_data, locale="en")
        assert "John Doe" in result
        assert "EMP456" in result
        assert "Sales" in result
        assert "Manager" in result

    def test_without_user_data(self, mock_tg_user):
        """Welcome message without user_data (new user)."""
        result = format_welcome_message(mock_tg_user, None, locale="en")
        assert "start.welcome_new" in result

    def test_user_without_last_name(self, mock_tg_user_no_last_name):
        """Welcome message for user without last name."""
        user_data = {
            "employee_id": "EMP789",
            "department": "HR",
            "position": "Recruiter",
        }
        result = format_welcome_message(mock_tg_user_no_last_name, user_data, locale="en")
        assert "Jane" in result
        assert "Doe" not in result
        assert "EMP789" in result

    def test_missing_fields_use_defaults(self, mock_tg_user):
        """Missing fields should use N/A defaults when user_data is non-empty."""
        user_data = {"employee_id": None}
        result = format_welcome_message(mock_tg_user, user_data, locale="en")
        assert "N/A" in result


class TestFormatChecklistProgress:
    """Test cases for format_checklist_progress function."""

    def test_completed_status_emoji(self):
        """Completed status should show checkmark emoji."""
        checklist = {
            "id": 1,
            "name": "Test Checklist",
            "progress_percentage": 100,
            "status": "completed",
            "total_tasks": 10,
            "completed_tasks": 10,
        }
        result = format_checklist_progress(checklist, locale="en")
        assert "\u2705" in result

    def test_in_progress_status_emoji(self):
        """In progress status should show arrows emoji."""
        checklist = {
            "id": 1,
            "name": "Test Checklist",
            "progress_percentage": 50,
            "status": "in_progress",
            "total_tasks": 10,
            "completed_tasks": 5,
        }
        result = format_checklist_progress(checklist, locale="en")
        assert "\U0001f504" in result

    def test_overdue_status_emoji(self):
        """Overdue status should show warning emoji."""
        checklist = {
            "id": 1,
            "name": "Test Checklist",
            "progress_percentage": 30,
            "status": "overdue",
            "total_tasks": 10,
            "completed_tasks": 3,
        }
        result = format_checklist_progress(checklist, locale="en")
        assert "\u26a0\ufe0f" in result

    def test_unknown_status_emoji(self):
        """Unknown status should show clipboard emoji."""
        checklist = {
            "id": 1,
            "name": "Test Checklist",
            "progress_percentage": 0,
            "status": "unknown",
            "total_tasks": 10,
            "completed_tasks": 0,
        }
        result = format_checklist_progress(checklist, locale="en")
        assert "\U0001f4cb" in result

    def test_progress_bar_at_0_percent(self):
        """Progress bar at 0% should be all empty."""
        checklist = {
            "id": 1,
            "name": "Test Checklist",
            "progress_percentage": 0,
            "status": "pending",
            "total_tasks": 10,
            "completed_tasks": 0,
        }
        result = format_checklist_progress(checklist, locale="en")
        assert "\u2591" in result
        assert "0%" in result

    def test_progress_bar_at_50_percent(self):
        """Progress bar at 50% should be half filled."""
        checklist = {
            "id": 1,
            "name": "Test Checklist",
            "progress_percentage": 50,
            "status": "in_progress",
            "total_tasks": 10,
            "completed_tasks": 5,
        }
        result = format_checklist_progress(checklist, locale="en")
        assert "50%" in result
        assert "\u2588" in result
        assert "\u2591" in result

    def test_progress_bar_at_100_percent(self):
        """Progress bar at 100% should be all filled."""
        checklist = {
            "id": 1,
            "name": "Test Checklist",
            "progress_percentage": 100,
            "status": "completed",
            "total_tasks": 10,
            "completed_tasks": 10,
        }
        result = format_checklist_progress(checklist, locale="en")
        assert "100%" in result
        assert "\u2588" in result

    def test_default_name_from_id(self):
        """When name is missing, should use ID-based default."""
        checklist = {
            "id": 42,
            "progress_percentage": 0,
            "status": "pending",
            "total_tasks": 5,
            "completed_tasks": 0,
        }
        result = format_checklist_progress(checklist, locale="en")
        assert "Checklist #42" in result


class TestFormatTaskList:
    """Test cases for format_task_list function."""

    def test_empty_task_list(self):
        """Empty task list should return translated message."""
        result = format_task_list([], locale="en")
        assert "checklists.no_tasks_general" in result

    def test_single_task_display(self):
        """Single task should be formatted correctly."""
        tasks = [
            {
                "id": 1,
                "title": "Test Task",
                "status": "pending",
                "category": "onboarding",
            }
        ]
        result = format_task_list(tasks, locale="en")
        assert "1." in result
        assert "Test Task" in result
        assert "onboarding" in result

    def test_task_status_emojis(self):
        """Different statuses should show correct emojis."""
        tasks = [
            {"id": 1, "title": "Completed", "status": "completed", "category": "test"},
            {"id": 2, "title": "In Progress", "status": "in_progress", "category": "test"},
            {"id": 3, "title": "Blocked", "status": "blocked", "category": "test"},
            {"id": 4, "title": "Overdue", "status": "overdue", "category": "test"},
            {"id": 5, "title": "Pending", "status": "pending", "category": "test"},
        ]
        result = format_task_list(tasks, locale="en")
        assert "\u2705" in result
        assert "\U0001f504" in result
        assert "\u26d4" in result
        assert "\u26a0\ufe0f" in result
        assert "\U0001f4dd" in result

    def test_truncation_at_max_displayed_tasks(self):
        """List should truncate at MAX_DISPLAYED_TASKS with more message."""
        tasks = [
            {"id": i, "title": f"Task {i}", "status": "pending", "category": "test"}
            for i in range(1, MAX_DISPLAYED_TASKS + 3)
        ]
        result = format_task_list(tasks, locale="en")
        more_count = len(tasks) - MAX_DISPLAYED_TASKS
        assert f"tasks.more_tasks|count={more_count}" in result or "..." in result


class TestFormatDate:
    """Test cases for format_date function."""

    def test_today(self):
        """Today should return 'Today'."""
        now = datetime.now(UTC)
        result = format_date(now)
        assert result == "Today"

    def test_yesterday(self):
        """Yesterday should return 'Yesterday'."""
        yesterday = datetime.now(UTC) - timedelta(days=1)
        result = format_date(yesterday)
        assert result == "Yesterday"

    def test_less_than_7_days_ago(self):
        """Less than 7 days ago should return 'X days ago'."""
        for days in [2, 3, 6]:
            dt = datetime.now(UTC) - timedelta(days=days)
            result = format_date(dt)
            assert result == f"{days} days ago"

    def test_older_than_7_days(self):
        """Older than 7 days should return formatted date."""
        old_date = datetime(2024, 1, 15, tzinfo=UTC)
        result = format_date(old_date)
        assert "Jan 15, 2024" in result or "Jan 15" in result


class TestFormatMeetingList:
    """Test cases for format_meeting_list function."""

    def test_empty_meeting_list(self):
        """Empty meeting list should return translated message."""
        result = format_meeting_list([], locale="en")
        assert "meetings.no_meetings_list" in result

    def test_meeting_with_valid_scheduled_at(self):
        """Meeting with valid scheduled_at should show formatted date."""
        meetings = [
            {
                "id": 1,
                "title": "Team Meeting",
                "scheduled_at": "2024-12-25T14:30:00",
                "meeting_type": "general",
            }
        ]
        result = format_meeting_list(meetings, locale="en")
        assert "Team Meeting" in result
        assert "25.12.2024 14:30" in result

    def test_meeting_with_none_scheduled_at(self):
        """Meeting with None scheduled_at should show 'TBD'."""
        meetings = [
            {
                "id": 1,
                "title": "Unscheduled Meeting",
                "scheduled_at": None,
                "meeting_type": "general",
            }
        ]
        result = format_meeting_list(meetings, locale="en")
        assert "Unscheduled Meeting" in result
        assert "TBD" in result

    def test_meeting_with_empty_scheduled_at(self):
        """Meeting with empty scheduled_at should show 'TBD'."""
        meetings = [
            {
                "id": 1,
                "title": "Empty Date Meeting",
                "scheduled_at": "",
                "meeting_type": "general",
            }
        ]
        result = format_meeting_list(meetings, locale="en")
        assert "TBD" in result

    def test_meeting_with_invalid_iso_date(self):
        """Meeting with invalid ISO date should show 'TBD'."""
        meetings = [
            {
                "id": 1,
                "title": "Bad Date Meeting",
                "scheduled_at": "not-a-valid-date",
                "meeting_type": "general",
            }
        ]
        result = format_meeting_list(meetings, locale="en")
        assert "TBD" in result

    def test_meeting_type_emojis(self):
        """Different meeting types should show correct emojis."""
        meetings = [
            {"id": 1, "title": "Onboarding", "scheduled_at": "2024-12-25T10:00:00", "meeting_type": "onboarding"},
            {"id": 2, "title": "Mentor", "scheduled_at": "2024-12-25T11:00:00", "meeting_type": "mentor"},
            {"id": 3, "title": "HR", "scheduled_at": "2024-12-25T12:00:00", "meeting_type": "hr"},
            {"id": 4, "title": "Technical", "scheduled_at": "2024-12-25T13:00:00", "meeting_type": "technical"},
            {"id": 5, "title": "General", "scheduled_at": "2024-12-25T14:00:00", "meeting_type": "general"},
        ]
        result = format_meeting_list(meetings, locale="en")
        assert "\U0001f44b" in result
        assert "\U0001f468\u200d\U0001f3eb" in result
        assert "\U0001f4de" in result
        assert "\U0001f4bb" in result
        assert "\U0001f4c5" in result


class TestAdditionalFormatters:
    """Test additional formatter functions."""

    def test_format_task_detail_exists(self):
        """Test that format_task_detail function exists and is importable."""
        from telegram_bot.utils.formatters import format_task_detail
        assert callable(format_task_detail)

    def test_format_search_results_exists(self):
        """Test that format_search_results function exists."""
        from telegram_bot.utils.formatters import format_search_results
        assert callable(format_search_results)

    def test_format_percentage_exists(self):
        """Test that format_percentage function exists."""
        from telegram_bot.utils.formatters import format_percentage
        assert callable(format_percentage)

    def test_format_feedback_menu_exists(self):
        """Test that format_feedback_menu function exists."""
        from telegram_bot.utils.formatters import format_feedback_menu
        assert callable(format_feedback_menu)

    def test_format_feedback_menu_output(self):
        """Test format_feedback_menu produces correct output."""
        from telegram_bot.utils.formatters import format_feedback_menu

        result = format_feedback_menu(locale="en")
        assert "feedback.title" in result or "Feedback" in result
        assert "feedback.description" in result or "share" in result
        assert "feedback.options" in result or "Options" in result

    def test_format_escalation_list_exists(self):
        """Test that format_escalation_list function exists."""
        from telegram_bot.utils.formatters import format_escalation_list
        assert callable(format_escalation_list)

    def test_format_percentage_output(self):
        """Test format_percentage produces correct output."""
        from telegram_bot.utils.formatters import format_percentage

        assert format_percentage(0) == "0.0%"
        assert format_percentage(50) == "50.0%"
        assert format_percentage(100) == "100.0%"

    def test_format_search_results_empty(self):
        """Test format_search_results with no results."""
        from telegram_bot.utils.formatters import format_search_results

        result = format_search_results("query", [], locale="en")
        assert "No results" in result

    def test_format_search_results_with_data(self):
        """Test format_search_results with results."""
        from telegram_bot.utils.formatters import format_search_results

        results = [
            {"title": "Article 1", "snippet": "Snippet 1", "category": "Help", "relevance": 0.9}
        ]
        result = format_search_results("query", results, locale="en")
        assert "Article 1" in result

    def test_format_task_detail_basic(self):
        """Test format_task_detail with basic task."""
        from telegram_bot.utils.formatters import format_task_detail

        task = {
            "id": 1,
            "title": "Test Task",
            "description": "Test Description",
            "status": "pending",
        }
        result = format_task_detail(task, locale="en")
        assert "Test Task" in result

    def test_format_escalation_list_empty(self):
        """Test format_escalation_list with empty list."""
        from telegram_bot.utils.formatters import format_escalation_list

        result = format_escalation_list([], locale="en")
        assert "escalation.no_escalations" in result or "Escalations" in result

    def test_format_escalation_list_with_data(self):
        """Test format_escalation_list with data."""
        from telegram_bot.utils.formatters import format_escalation_list

        escalations = [
            {"id": 1, "title": "Issue 1", "status": "open", "category": "Tech", "created_at": "2024-12-01"}
        ]
        result = format_escalation_list(escalations, locale="en")
        assert "Issue 1" in result


class TestFormattersEdgeCases:
    """Test edge cases for formatter functions."""

    def test_format_task_list_invalid_due_date(self):
        """Test format_task_list with invalid due date format."""
        from telegram_bot.utils.formatters import format_task_list

        tasks = [
            {"id": 1, "title": "Task 1", "status": "pending", "category": "test", "due_date": "invalid-date"}
        ]
        result = format_task_list(tasks, locale="en")
        # Should not include due date for invalid format
        assert "Task 1" in result

    def test_format_task_list_valid_due_date(self):
        """Test format_task_list with valid due date includes formatted date."""
        from telegram_bot.utils.formatters import format_task_list

        tasks = [
            {
                "id": 1,
                "title": "Task with Due",
                "status": "pending",
                "category": "test",
                "due_date": "2024-12-25T14:30:00",
            }
        ]
        result = format_task_list(tasks, locale="en")
        # Should include the formatted due date
        assert "Task with Due" in result
        assert "Dec 25" in result  # Due date formatted

    def test_format_task_detail_overdue_task(self):
        """Test format_task_detail with overdue pending task."""
        from telegram_bot.utils.formatters import format_task_detail

        # Create a task with past due date and pending status
        past_date = "2020-01-01T00:00:00+00:00"
        task = {
            "id": 1,
            "title": "Overdue Task",
            "description": "Description",
            "status": "pending",
            "due_date": past_date,
        }
        result = format_task_detail(task, locale="en")
        assert "Overdue Task" in result

    def test_format_task_detail_with_dependencies(self):
        """Test format_task_detail with dependencies."""
        from telegram_bot.utils.formatters import format_task_detail

        task = {
            "id": 1,
            "title": "Task with deps",
            "description": "Description",
            "status": "pending",
            "depends_on": [{"id": 1}, {"id": 2}],
        }
        result = format_task_detail(task, locale="en")
        assert "Task with deps" in result

    def test_format_task_detail_with_assignee(self):
        """Test format_task_detail with assignee."""
        from telegram_bot.utils.formatters import format_task_detail

        task = {
            "id": 1,
            "title": "Assigned Task",
            "description": "Description",
            "status": "pending",
            "assignee": "John Doe",
        }
        result = format_task_detail(task, locale="en")
        assert "Assigned Task" in result
        assert "John Doe" in result

    def test_format_task_detail_invalid_due_date(self):
        """Test format_task_detail with invalid due date."""
        from telegram_bot.utils.formatters import format_task_detail

        task = {
            "id": 1,
            "title": "Task",
            "description": "Description",
            "status": "pending",
            "due_date": "not-a-date",
        }
        result = format_task_detail(task, locale="en")
        assert "Task" in result

    def test_format_search_results_more_results_hidden(self):
        """Test format_search_results with more results than displayed."""
        from telegram_bot.utils.formatters import MAX_SEARCH_RESULTS_DISPLAY, format_search_results

        results = [
            {"title": f"Article {i}", "snippet": f"Snippet {i}", "category": "Help", "relevance": 0.5}
            for i in range(MAX_SEARCH_RESULTS_DISPLAY + 3)
        ]
        result = format_search_results("query", results, locale="en")
        assert "more results not shown" in result

    def test_format_meeting_list_more_meetings(self):
        """Test format_meeting_list with more meetings than displayed."""
        from telegram_bot.utils.formatters import MAX_DISPLAYED_MEETINGS, format_meeting_list

        meetings = [
            {"id": i, "title": f"Meeting {i}", "scheduled_at": "2024-12-25T10:00:00", "meeting_type": "general"}
            for i in range(MAX_DISPLAYED_MEETINGS + 2)
        ]
        result = format_meeting_list(meetings, locale="en")
        assert "more meetings" in result

    def test_format_escalation_list_more_escalations(self):
        """Test format_escalation_list with more escalations than displayed."""
        from telegram_bot.utils.formatters import MAX_DISPLAYED_ESCALATIONS, format_escalation_list

        escalations = [
            {"id": i, "title": f"Issue {i}", "status": "open", "category": "Tech", "created_at": "2024-12-01"}
            for i in range(MAX_DISPLAYED_ESCALATIONS + 2)
        ]
        result = format_escalation_list(escalations, locale="en")
        assert "more escalations" in result

    def test_format_escalation_list_invalid_created_at(self):
        """Test format_escalation_list with invalid created_at date."""
        from telegram_bot.utils.formatters import format_escalation_list

        escalations = [
            {"id": 1, "title": "Issue 1", "status": "open", "category": "Tech", "created_at": "not-a-date"}
        ]
        result = format_escalation_list(escalations, locale="en")
        assert "Issue 1" in result
