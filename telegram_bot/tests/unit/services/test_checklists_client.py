"""Unit tests for telegram_bot/services/checklists_client.py."""

from unittest.mock import MagicMock, patch

import pytest

from telegram_bot.services.checklists_client import ChecklistsServiceClient, checklists_client


class TestChecklistsServiceClient:
    """Test cases for ChecklistsServiceClient."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test client."""
        self.client = ChecklistsServiceClient(base_url="http://test-checklists:8002")
        self.auth_token = "test_token_123"
        self.user_id = 1

    @patch("telegram_bot.services.checklists_client.httpx.AsyncClient.get")
    async def test_get_user_checklists_success(self, mock_get):
        """Test getting user checklists - success."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "checklists": [
                {"id": 1, "name": "Onboarding", "progress_percentage": 50},
                {"id": 2, "name": "Training", "progress_percentage": 30},
            ]
        }
        mock_get.return_value = mock_response

        result = await self.client.get_user_checklists(self.user_id, self.auth_token)

        assert len(result) == 2

    @patch("telegram_bot.services.checklists_client.httpx.AsyncClient.get")
    async def test_get_user_checklists_request_error(self, mock_get):
        """Test getting user checklists - request error."""
        import httpx
        mock_get.side_effect = httpx.RequestError("Connection failed")

        result = await self.client.get_user_checklists(self.user_id, self.auth_token)

        assert result == []

    @patch("telegram_bot.services.checklists_client.httpx.AsyncClient.get")
    async def test_get_checklist_tasks_success(self, mock_get):
        """Test getting checklist tasks - success."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {"id": 1, "title": "Task 1", "status": "PENDING"},
            {"id": 2, "title": "Task 2", "status": "COMPLETED"},
        ]
        mock_get.return_value = mock_response

        result = await self.client.get_checklist_tasks(1, self.auth_token)

        assert len(result) == 2

    @patch("telegram_bot.services.checklists_client.httpx.AsyncClient.get")
    async def test_get_assigned_tasks_success(self, mock_get):
        """Test getting assigned tasks - success."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {"id": 1, "title": "Task 1", "status": "IN_PROGRESS"},
        ]
        mock_get.return_value = mock_response

        result = await self.client.get_assigned_tasks(self.auth_token)

        assert len(result) == 1

    @patch("telegram_bot.services.checklists_client.httpx.AsyncClient.put")
    async def test_update_task_status_success(self, mock_put):
        """Test updating task status - success."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"id": 1, "status": "IN_PROGRESS"}
        mock_put.return_value = mock_response

        result = await self.client.update_task_status(1, "in_progress", self.auth_token)

        assert result is not None

    @patch("telegram_bot.services.checklists_client.httpx.AsyncClient.post")
    async def test_complete_task_success(self, mock_post):
        """Test completing task - success."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"id": 1, "status": "COMPLETED"}
        mock_post.return_value = mock_response

        result = await self.client.complete_task(1, self.auth_token, "Completed via bot")

        assert result is not None

    @patch("telegram_bot.services.checklists_client.httpx.AsyncClient.get")
    async def test_get_checklist_progress_success(self, mock_get):
        """Test getting checklist progress - success."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "progress_percentage": 75,
            "completed_tasks": 6,
            "total_tasks": 8,
        }
        mock_get.return_value = mock_response

        result = await self.client.get_checklist_progress(1, self.auth_token)

        assert result is not None

    @patch("telegram_bot.services.checklists_client.httpx.AsyncClient.get")
    async def test_get_templates_success(self, mock_get):
        """Test getting checklist templates - success."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {"id": 1, "name": "Developer Onboarding"},
            {"id": 2, "name": "Manager Onboarding"},
        ]
        mock_get.return_value = mock_response

        result = await self.client.get_templates(self.auth_token)

        assert len(result) == 2

    @patch("telegram_bot.services.checklists_client.httpx.AsyncClient.get")
    async def test_get_overdue_tasks_success(self, mock_get):
        """Test getting overdue tasks - success."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {"id": 1, "title": "Overdue Task", "due_date": "2024-01-01"},
        ]
        mock_get.return_value = mock_response

        result = await self.client.get_overdue_tasks(self.auth_token)

        assert len(result) == 1

    @patch("telegram_bot.services.checklists_client.httpx.AsyncClient.get")
    async def test_get_admin_stats_success(self, mock_get):
        """Test getting admin stats - success."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "active_checklists": 10,
            "completed_tasks": 50,
            "pending_tasks": 20,
        }
        mock_get.return_value = mock_response

        result = await self.client.get_admin_stats(self.auth_token)

        assert result["active_checklists"] == 10

    @patch("telegram_bot.services.checklists_client.httpx.AsyncClient.get")
    async def test_get_admin_stats_error(self, mock_get):
        """Test getting admin stats - error returns defaults."""
        import httpx
        mock_get.side_effect = httpx.RequestError("Connection failed")

        result = await self.client.get_admin_stats(self.auth_token)

        assert result["active_checklists"] == 0

    @patch("telegram_bot.services.checklists_client.httpx.AsyncClient.post")
    async def test_upload_task_attachment_success(self, mock_post):
        """Test uploading task attachment - success."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"id": 1, "filename": "test.pdf"}
        mock_post.return_value = mock_response

        result = await self.client.upload_task_attachment(
            task_id=1,
            file_content=b"file content",
            filename="test.pdf",
            auth_token=self.auth_token,
            description="Test file"
        )

        assert result is not None

    @patch("telegram_bot.services.checklists_client.httpx.AsyncClient.get")
    async def test_get_task_attachments_success(self, mock_get):
        """Test getting task attachments - success."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {"id": 1, "filename": "file1.pdf"},
            {"id": 2, "filename": "file2.doc"},
        ]
        mock_get.return_value = mock_response

        result = await self.client.get_task_attachments(1, self.auth_token)

        assert len(result) == 2

    @patch("telegram_bot.services.checklists_client.httpx.AsyncClient.get")
    async def test_download_task_attachment_success(self, mock_get):
        """Test downloading task attachment - success."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.content = b"file content"
        mock_get.return_value = mock_response

        result = await self.client.download_task_attachment(1, "file.pdf", self.auth_token)

        assert result == b"file content"

    async def test_invalidate_task_cache(self):
        """Test invalidating task cache."""
        with patch("telegram_bot.services.checklists_client.invalidate_cache") as mock_invalidate:
            mock_invalidate.return_value = 5
            await self.client.invalidate_task_cache(self.auth_token, 1)

    @patch("telegram_bot.services.checklists_client.httpx.AsyncClient.get")
    async def test_get_task_details_from_assigned(self, mock_get):
        """Test getting task details from assigned tasks."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {"id": 1, "title": "Task 1", "status": "PENDING"},
        ]
        mock_get.return_value = mock_response

        result = await self.client.get_task_details(1, self.auth_token)

        assert result is not None

    @patch("telegram_bot.services.checklists_client.httpx.AsyncClient.put")
    async def test_start_task_success(self, mock_put):
        """Test starting task - success."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"id": 1, "status": "IN_PROGRESS"}
        mock_put.return_value = mock_response

        result = await self.client.start_task(1, self.auth_token)

        assert result is not None


class TestChecklistsClientSingleton:
    """Test the checklists_client singleton."""

    def test_singleton_exists(self):
        """Test that singleton exists."""
        assert checklists_client is not None


class TestChecklistsClientEdgeCases:
    """Test edge cases and error handling for ChecklistsServiceClient."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test client."""
        self.client = ChecklistsServiceClient(base_url="http://test-checklists:8002")
        self.auth_token = "test_token_123"
        self.user_id = 1

    @patch("telegram_bot.services.checklists_client.httpx.AsyncClient.get")
    async def test_get_user_checklists_non_200_status(self, mock_get):
        """Test getting user checklists with non-200 status codes."""
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response

        result = await self.client.get_user_checklists(self.user_id, self.auth_token)

        assert result == []

    @patch("telegram_bot.services.checklists_client.httpx.AsyncClient.get")
    async def test_get_user_checklists_500_error(self, mock_get):
        """Test getting user checklists with 500 error."""
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_get.return_value = mock_response

        result = await self.client.get_user_checklists(self.user_id, self.auth_token)

        assert result == []

    @patch("telegram_bot.services.checklists_client.httpx.AsyncClient.get")
    async def test_get_checklist_tasks_request_error(self, mock_get):
        """Test getting checklist tasks with request error."""
        import httpx
        mock_get.side_effect = httpx.RequestError("Connection failed")

        result = await self.client.get_checklist_tasks(1, self.auth_token)

        assert result == []

    @patch("telegram_bot.services.checklists_client.httpx.AsyncClient.get")
    async def test_get_assigned_tasks_non_200(self, mock_get):
        """Test getting assigned tasks with non-200 status."""
        mock_response = MagicMock()
        mock_response.status_code = 403
        mock_get.return_value = mock_response

        result = await self.client.get_assigned_tasks(self.auth_token)

        assert result == []

    @patch("telegram_bot.services.checklists_client.httpx.AsyncClient.get")
    async def test_get_assigned_tasks_request_error(self, mock_get):
        """Test getting assigned tasks with request error."""
        import httpx
        mock_get.side_effect = httpx.RequestError("Timeout")

        result = await self.client.get_assigned_tasks(self.auth_token)

        assert result == []

    @patch("telegram_bot.services.checklists_client.httpx.AsyncClient.put")
    async def test_update_task_status_non_200(self, mock_put):
        """Test updating task status with non-200 status."""
        mock_response = MagicMock()
        mock_response.status_code = 422
        mock_response.text = "Validation error"
        mock_put.return_value = mock_response

        result = await self.client.update_task_status(1, "in_progress", self.auth_token)

        assert result is None

    @patch("telegram_bot.services.checklists_client.httpx.AsyncClient.put")
    async def test_update_task_status_request_error(self, mock_put):
        """Test updating task status with request error."""
        import httpx
        mock_put.side_effect = httpx.RequestError("Network error")

        result = await self.client.update_task_status(1, "in_progress", self.auth_token)

        assert result is None

    @patch("telegram_bot.services.checklists_client.httpx.AsyncClient.put")
    async def test_update_task_status_logs_error(self, mock_put):
        """Test that update task status logs error response."""
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.text = "Bad request details"
        mock_put.return_value = mock_response

        with patch("telegram_bot.services.checklists_client.logger") as mock_logger:
            result = await self.client.update_task_status(1, "in_progress", self.auth_token)

            assert result is None
            mock_logger.error.assert_called()

    @patch("telegram_bot.services.checklists_client.httpx.AsyncClient.post")
    async def test_complete_task_non_200(self, mock_post):
        """Test completing task with non-200 status."""
        mock_response = MagicMock()
        mock_response.status_code = 403
        mock_response.text = "Forbidden"
        mock_post.return_value = mock_response

        result = await self.client.complete_task(1, self.auth_token, "Done")

        assert result is None

    @patch("telegram_bot.services.checklists_client.httpx.AsyncClient.post")
    async def test_complete_task_request_error(self, mock_post):
        """Test completing task with request error."""
        import httpx
        mock_post.side_effect = httpx.RequestError("Connection lost")

        result = await self.client.complete_task(1, self.auth_token)

        assert result is None

    @patch("telegram_bot.services.checklists_client.httpx.AsyncClient.get")
    async def test_get_checklist_progress_non_200(self, mock_get):
        """Test getting checklist progress with non-200 status."""
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response

        result = await self.client.get_checklist_progress(1, self.auth_token)

        assert result is None

    @patch("telegram_bot.services.checklists_client.httpx.AsyncClient.get")
    async def test_get_checklist_progress_request_error(self, mock_get):
        """Test getting checklist progress with request error."""
        import httpx
        mock_get.side_effect = httpx.RequestError("Server unavailable")

        result = await self.client.get_checklist_progress(1, self.auth_token)

        assert result is None

    @patch("telegram_bot.services.checklists_client.httpx.AsyncClient.get")
    async def test_get_templates_non_200(self, mock_get):
        """Test getting templates with non-200 status."""
        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_get.return_value = mock_response

        result = await self.client.get_templates(self.auth_token)

        assert result == []

    @patch("telegram_bot.services.checklists_client.httpx.AsyncClient.get")
    async def test_get_templates_request_error(self, mock_get):
        """Test getting templates with request error."""
        import httpx
        mock_get.side_effect = httpx.RequestError("Timeout")

        result = await self.client.get_templates(self.auth_token)

        assert result == []

    @patch("telegram_bot.services.checklists_client.httpx.AsyncClient.get")
    async def test_get_overdue_tasks_non_200(self, mock_get):
        """Test getting overdue tasks with non-200 status."""
        mock_response = MagicMock()
        mock_response.status_code = 403
        mock_get.return_value = mock_response

        result = await self.client.get_overdue_tasks(self.auth_token)

        assert result == []

    @patch("telegram_bot.services.checklists_client.httpx.AsyncClient.get")
    async def test_get_overdue_tasks_request_error(self, mock_get):
        """Test getting overdue tasks with request error."""
        import httpx
        mock_get.side_effect = httpx.RequestError("Network error")

        result = await self.client.get_overdue_tasks(self.auth_token)

        assert result == []

    @patch("telegram_bot.services.checklists_client.httpx.AsyncClient.get")
    async def test_get_task_details_not_in_assigned_or_checklist(self, mock_get):
        """Test getting task details when task not found."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        # Task not in assigned tasks
        mock_response.json.return_value = [{"id": 999, "title": "Other task"}]
        mock_get.return_value = mock_response

        result = await self.client.get_task_details(1, self.auth_token, checklist_id=None)

        assert result is None

    @patch("telegram_bot.services.checklists_client.httpx.AsyncClient.get")
    async def test_get_task_details_with_checklist_id_not_found(self, mock_get):
        """Test getting task details from checklist when not found."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        # First call returns assigned tasks, second returns checklist tasks
        mock_response.json.side_effect = [
            [{"id": 999, "title": "Other task"}],  # assigned tasks
            [{"id": 888, "title": "Another task"}],  # checklist tasks
        ]
        mock_get.return_value = mock_response

        result = await self.client.get_task_details(1, self.auth_token, checklist_id=10)

        assert result is None

    @patch("telegram_bot.services.checklists_client.httpx.AsyncClient.get")
    async def test_get_task_details_checklist_id_task_not_in_list(self, mock_get):
        """Test get_task_details when checklist_id provided but task not found in checklist tasks.

        When checklist_id is provided, get_checklist_tasks returns tasks,
        but none match the task_id - should fall through to return None.
        """
        mock_response = MagicMock()
        mock_response.status_code = 200
        # First call (assigned tasks): no matching task
        # Second call (checklist tasks): returns tasks but not the one we're looking for
        mock_response.json.side_effect = [
            [{"id": 100, "title": "Other assigned task"}],  # assigned tasks - no match
            [{"id": 200, "title": "Checklist task 1"}, {"id": 300, "title": "Checklist task 2"}],  # checklist tasks - no match for task_id=1
        ]
        mock_get.return_value = mock_response

        result = await self.client.get_task_details(1, self.auth_token, checklist_id=10)

        assert result is None

    @patch("telegram_bot.services.checklists_client.httpx.AsyncClient.get")
    async def test_get_task_details_found_in_checklist_tasks(self, mock_get):
        """Test get_task_details when task is found in checklist tasks (line 150).

        Covers line 150: when checklist_id is provided and task IS found in checklist tasks,
        the method returns the task from the checklist lookup.
        """
        mock_response = MagicMock()
        mock_response.status_code = 200
        target_task = {"id": 1, "title": "Target Task in Checklist", "status": "PENDING"}
        # First call (assigned tasks): no matching task
        # Second call (checklist tasks): returns tasks including the target
        mock_response.json.side_effect = [
            [{"id": 100, "title": "Other assigned task"}],  # assigned tasks - no match
            [{"id": 200, "title": "Checklist task 1"}, target_task, {"id": 300, "title": "Checklist task 2"}],  # checklist tasks - includes task_id=1
        ]
        mock_get.return_value = mock_response

        result = await self.client.get_task_details(1, self.auth_token, checklist_id=10)

        assert result is not None
        assert result["id"] == 1
        assert result["title"] == "Target Task in Checklist"

    @patch("telegram_bot.services.checklists_client.httpx.AsyncClient.get")
    async def test_get_task_details_request_error(self, mock_get):
        """Test getting task details with request error."""
        import httpx
        mock_get.side_effect = httpx.RequestError("Error")

        result = await self.client.get_task_details(1, self.auth_token)

        assert result is None

    @patch("telegram_bot.services.checklists_client.httpx.AsyncClient.post")
    async def test_upload_task_attachment_non_200(self, mock_post):
        """Test uploading attachment with non-200 status."""
        mock_response = MagicMock()
        mock_response.status_code = 413  # Payload too large
        mock_response.text = "File too large"
        mock_post.return_value = mock_response

        result = await self.client.upload_task_attachment(
            task_id=1,
            file_content=b"file content",
            filename="test.pdf",
            auth_token=self.auth_token,
        )

        assert result is None

    @patch("telegram_bot.services.checklists_client.httpx.AsyncClient.post")
    async def test_upload_task_attachment_request_error(self, mock_post):
        """Test uploading attachment with request error."""
        import httpx
        mock_post.side_effect = httpx.RequestError("Upload failed")

        result = await self.client.upload_task_attachment(
            task_id=1,
            file_content=b"file content",
            filename="test.pdf",
            auth_token=self.auth_token,
        )

        assert result is None

    @patch("telegram_bot.services.checklists_client.httpx.AsyncClient.post")
    async def test_upload_task_attachment_with_bytesio(self, mock_post):
        """Test uploading attachment with BytesIO object."""
        from io import BytesIO

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"id": 1, "filename": "test.pdf"}
        mock_post.return_value = mock_response

        file_obj = BytesIO(b"file content")
        result = await self.client.upload_task_attachment(
            task_id=1,
            file_content=file_obj,
            filename="test.pdf",
            auth_token=self.auth_token,
        )

        assert result is not None

    @patch("telegram_bot.services.checklists_client.httpx.AsyncClient.get")
    async def test_get_task_attachments_non_200(self, mock_get):
        """Test getting attachments with non-200 status."""
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response

        result = await self.client.get_task_attachments(1, self.auth_token)

        assert result == []

    @patch("telegram_bot.services.checklists_client.httpx.AsyncClient.get")
    async def test_get_task_attachments_request_error(self, mock_get):
        """Test getting attachments with request error."""
        import httpx
        mock_get.side_effect = httpx.RequestError("Error")

        result = await self.client.get_task_attachments(1, self.auth_token)

        assert result == []

    @patch("telegram_bot.services.checklists_client.httpx.AsyncClient.get")
    async def test_download_task_attachment_non_200(self, mock_get):
        """Test downloading attachment with non-200 status."""
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response

        result = await self.client.download_task_attachment(1, "file.pdf", self.auth_token)

        assert result is None

    @patch("telegram_bot.services.checklists_client.httpx.AsyncClient.get")
    async def test_download_task_attachment_request_error(self, mock_get):
        """Test downloading attachment with request error."""
        import httpx
        mock_get.side_effect = httpx.RequestError("Download failed")

        result = await self.client.download_task_attachment(1, "file.pdf", self.auth_token)

        assert result is None

    async def test_invalidate_task_cache_without_checklist_id(self):
        """Test invalidating cache without checklist_id."""
        with patch("telegram_bot.services.checklists_client.invalidate_cache") as mock_invalidate:
            mock_invalidate.return_value = 3
            await self.client.invalidate_task_cache(self.auth_token, None)

            # Should only invalidate assigned_tasks pattern
            mock_invalidate.assert_called_once()
            call_args = mock_invalidate.call_args[0][0]
            assert "assigned_tasks" in call_args

    @patch("telegram_bot.services.checklists_client.httpx.AsyncClient.get")
    async def test_get_checklist_tasks_non_200(self, mock_get):
        """Test getting checklist tasks with non-200 status."""
        mock_response = MagicMock()
        mock_response.status_code = 403
        mock_get.return_value = mock_response

        result = await self.client.get_checklist_tasks(1, self.auth_token)

        assert result == []

    @patch("telegram_bot.services.checklists_client.httpx.AsyncClient.post")
    async def test_complete_task_without_notes(self, mock_post):
        """Test completing task without completion notes."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"id": 1, "status": "COMPLETED"}
        mock_post.return_value = mock_response

        result = await self.client.complete_task(1, self.auth_token, notes=None)

        assert result is not None
        # Verify params not included when notes is None
        call_kwargs = mock_post.call_args.kwargs
        assert call_kwargs.get("params") is None

    @patch("telegram_bot.services.checklists_client.logger")
    @patch("telegram_bot.services.checklists_client.httpx.AsyncClient.post")
    async def test_upload_task_attachment_logs_error(self, mock_post, mock_logger):
        """Test that upload error is logged."""
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.text = "Error message that is quite long and should be truncated"
        mock_post.return_value = mock_response

        result = await self.client.upload_task_attachment(
            task_id=1,
            file_content=b"content",
            filename="test.pdf",
            auth_token=self.auth_token,
        )

        assert result is None
        mock_logger.error.assert_called()

    @patch("telegram_bot.services.checklists_client.httpx.AsyncClient.get")
    async def test_get_admin_stats_non_200_various_codes(self, mock_get):
        """Test getting admin stats with various non-200 codes."""
        for status_code in [401, 403, 404, 500, 502, 503]:
            mock_response = MagicMock()
            mock_response.status_code = status_code
            mock_get.return_value = mock_response

            result = await self.client.get_admin_stats(self.auth_token)

            assert result["active_checklists"] == 0
            assert result["completed_tasks"] == 0
            assert result["pending_tasks"] == 0
