"""Checklist management service with repository pattern."""

import uuid
from datetime import UTC, datetime, timedelta
from typing import Any, cast

from loguru import logger

from checklists_service.core import NotFoundException, ValidationException
from checklists_service.core.enums import ChecklistStatus, TaskStatus, TemplateStatus
from checklists_service.models import Certificate, Checklist, Task
from checklists_service.repositories.unit_of_work import IUnitOfWork
from checklists_service.schemas import ChecklistCreate, ChecklistStats, ChecklistUpdate
from checklists_service.utils import auth_service_client, notification_service_client


class ChecklistService:
    """Service for checklist management operations with repository pattern."""

    def __init__(self, uow: IUnitOfWork, auth_token: str | None = None) -> None:
        """Initialize checklist service with Unit of Work and auth token."""
        self._uow = uow
        self.auth_token = auth_token

    async def _validate_user(self, user_id: int) -> dict:
        """Validate user exists in auth service."""
        if not self.auth_token:
            logger.warning("_validate_user called without auth token (user_id={})", user_id)
            msg = "Authentication required"
            raise ValidationException(msg)

        user_data = await auth_service_client.get_user(user_id, self.auth_token)
        if not user_data:
            logger.warning("User not found in auth service (user_id={})", user_id)
            msg = f"User {user_id} not found in auth service"
            raise ValidationException(msg)

        return user_data

    async def create_checklist(self, checklist_data: ChecklistCreate, auth_token: str) -> Checklist:
        """Create new checklist from template."""
        self.auth_token = auth_token
        logger.debug(
            "Creating checklist (user_id={}, template_id={}, mentor_id={}, hr_id={})",
            checklist_data.user_id,
            checklist_data.template_id,
            checklist_data.mentor_id,
            checklist_data.hr_id,
        )

        user_data = await self._validate_user(checklist_data.user_id)

        if user_data.get("employee_id") != checklist_data.employee_id:
            logger.warning(
                "Create checklist failed: employee_id mismatch (user_id={}, requested_employee_id={})",
                checklist_data.user_id,
                checklist_data.employee_id,
            )
            msg = "Employee ID does not match user"
            raise ValidationException(msg)

        template = await self._uow.templates.get_by_id(checklist_data.template_id)
        if not template or template.status != TemplateStatus.ACTIVE:
            logger.warning(
                "Create checklist failed: template not active (template_id={})",
                checklist_data.template_id,
            )
            msg = "Template not found or not active"
            raise ValidationException(msg)

        existing_checklist = await self._uow.checklists.get_by_user_and_template(
            checklist_data.user_id, checklist_data.template_id
        )
        if existing_checklist:
            logger.warning(
                "Create checklist conflict: already exists (user_id={}, template_id={}, existing_id={})",
                checklist_data.user_id,
                checklist_data.template_id,
                existing_checklist.id,
            )
            msg = "User already has a checklist for this template"
            raise ValidationException(msg)

        if checklist_data.mentor_id:
            mentor_data = await auth_service_client.get_user(checklist_data.mentor_id, auth_token)
            if not mentor_data:
                logger.warning(
                    "Create checklist: mentor not found (mentor_id={})",
                    checklist_data.mentor_id,
                )
                msg = f"Mentor {checklist_data.mentor_id} not found"
                raise ValidationException(msg)
            if mentor_data.get("role") not in ["MENTOR", "HR", "ADMIN"]:
                logger.warning(
                    "Create checklist: invalid mentor role (mentor_id={}, role={})",
                    checklist_data.mentor_id,
                    mentor_data.get("role"),
                )
                msg = "Mentor must have MENTOR, HR or ADMIN role"
                raise ValidationException(msg)

        if checklist_data.hr_id:
            hr_data = await auth_service_client.get_user(checklist_data.hr_id, auth_token)
            if not hr_data:
                logger.warning("Create checklist: HR not found (hr_id={})", checklist_data.hr_id)
                msg = f"HR {checklist_data.hr_id} not found"
                raise ValidationException(msg)
            if hr_data.get("role") not in ["HR", "ADMIN"]:
                logger.warning(
                    "Create checklist: invalid HR role (hr_id={}, role={})",
                    checklist_data.hr_id,
                    hr_data.get("role"),
                )
                msg = "HR must have HR or ADMIN role"
                raise ValidationException(msg)

        start_date = checklist_data.start_date or datetime.now(UTC)
        due_date = checklist_data.due_date or start_date + timedelta(days=template.duration_days)

        checklist = Checklist(
            user_id=checklist_data.user_id,
            employee_id=checklist_data.employee_id,
            template_id=checklist_data.template_id,
            start_date=start_date,
            due_date=due_date,
            mentor_id=checklist_data.mentor_id,
            hr_id=checklist_data.hr_id,
            notes=checklist_data.notes,
            status=ChecklistStatus.IN_PROGRESS,
            total_tasks=0,
        )

        checklist = await self._uow.checklists.create(checklist)

        task_templates = list(await self._uow.task_templates.find_by_template(template.id))

        tasks: list[Task] = []
        for _idx, task_template in enumerate(task_templates):
            task_due_date = start_date + timedelta(days=task_template.due_days)
            task_due_date = min(task_due_date, due_date)

            assignee_id = None
            if task_template.auto_assign and task_template.assignee_role:
                if task_template.assignee_role == "MENTOR" and checklist.mentor_id:
                    assignee_id = checklist.mentor_id
                elif task_template.assignee_role == "HR" and checklist.hr_id:
                    assignee_id = checklist.hr_id

            task = Task(
                checklist_id=cast("int", checklist.id),
                template_task_id=cast("int", task_template.id),
                title=task_template.title,
                description=task_template.description,
                category=task_template.category,
                order=task_template.order,
                due_date=task_due_date,
                assignee_id=assignee_id,
                assignee_role=task_template.assignee_role or template.default_assignee_role,
                depends_on=task_template.depends_on.copy(),
                blocks=[],
            )
            tasks.append(task)

        task_map = {task.template_task_id: task for task in tasks if task.template_task_id}
        for task in tasks:
            if task.depends_on:
                for dep_id in task.depends_on:
                    if dep_id in task_map and task.template_task_id:
                        task_map[dep_id].blocks.append(task.template_task_id)

        for task in tasks:
            await self._uow.tasks.create(task)

        checklist.total_tasks = len(tasks)
        updated_checklist = await self._uow.checklists.update(checklist)
        logger.info(
            "Checklist created (checklist_id={}, user_id={}, template_id={}, total_tasks={})",
            updated_checklist.id,
            updated_checklist.user_id,
            updated_checklist.template_id,
            updated_checklist.total_tasks,
        )
        return updated_checklist

    async def get_checklist(self, checklist_id: int) -> Checklist:
        """Get checklist by ID."""
        checklist = await self._uow.checklists.get_by_id(checklist_id)
        if not checklist:
            logger.warning("Checklist not found (checklist_id={})", checklist_id)
            msg = "Checklist"
            raise NotFoundException(msg)
        return checklist

    async def update_checklist(self, checklist_id: int, update_data: ChecklistUpdate) -> Checklist:
        """Update checklist."""
        logger.debug("Updating checklist (checklist_id={})", checklist_id)
        checklist = await self.get_checklist(checklist_id)

        if update_data.status == ChecklistStatus.COMPLETED and checklist.status != ChecklistStatus.COMPLETED:
            logger.info(
                "Checklist transitioning to COMPLETED via update (checklist_id={})",
                checklist_id,
            )
            checklist.completed_at = datetime.now(UTC)

            pending_tasks = list(await self._uow.tasks.find_by_checklist(checklist_id, status=TaskStatus.PENDING.value))
            in_progress_tasks = list(
                await self._uow.tasks.find_by_checklist(checklist_id, status=TaskStatus.IN_PROGRESS.value)
            )
            blocked_tasks = list(await self._uow.tasks.find_by_checklist(checklist_id, status=TaskStatus.BLOCKED.value))

            for task in pending_tasks + in_progress_tasks + blocked_tasks:
                task.status = TaskStatus.COMPLETED
                task.completed_at = datetime.now(UTC)

        if update_data.progress_percentage is not None:
            checklist.progress_percentage = update_data.progress_percentage

        for field, value in update_data.model_dump(exclude_unset=True).items():
            if field != "progress_percentage":
                setattr(checklist, field, value)

        await self._uow.checklists.recalculate_progress(checklist_id)

        checklist.updated_at = datetime.now(UTC)
        updated = await self._uow.checklists.update(checklist)
        logger.info("Checklist updated (checklist_id={})", updated.id)
        return updated

    async def delete_checklist(self, checklist_id: int) -> None:
        """Delete checklist."""
        checklist = await self.get_checklist(checklist_id)

        if checklist.status == ChecklistStatus.IN_PROGRESS:
            logger.warning("Delete rejected: checklist is IN_PROGRESS (checklist_id={})", checklist_id)
            msg = "Cannot delete in-progress checklist"
            raise ValidationException(msg)

        await self._uow.checklists.delete(checklist_id)
        logger.info("Checklist deleted (checklist_id={})", checklist_id)

    async def get_checklists(
        self,
        skip: int = 0,
        limit: int = 50,
        user_id: int | None = None,
        status: str | None = None,
        department_id: int | None = None,
        search: str | None = None,
        *,
        overdue_only: bool = False,
        sort_by: str | None = None,
        sort_order: str = "desc",
    ) -> tuple[list[Checklist], int]:
        """Get paginated list of checklists with filters."""
        status_enum = ChecklistStatus(status) if status else None

        checklists, total = await self._uow.checklists.find_checklists(
            skip=skip,
            limit=limit,
            user_id=user_id,
            status=status_enum,
            department_id=department_id,
            search=search,
            overdue_only=overdue_only,
            sort_by=sort_by,
            sort_order=sort_order,
        )
        return list(checklists), total

    async def complete_checklist(self, checklist_id: int) -> Checklist:
        """Mark checklist as completed and auto-issue certificate."""
        checklist = await self.get_checklist(checklist_id)

        if checklist.status == ChecklistStatus.COMPLETED:
            logger.debug("complete_checklist: already completed (checklist_id={})", checklist_id)
            return checklist

        status_counts = await self._uow.tasks.count_by_status(checklist_id)
        pending_tasks = sum(
            count for status_val, count in status_counts.items() if status_val != TaskStatus.COMPLETED.value
        )

        if pending_tasks > 0:
            logger.warning(
                "Cannot complete checklist: {} pending tasks (checklist_id={})",
                pending_tasks,
                checklist_id,
            )
            msg = "Cannot complete checklist with pending tasks"
            raise ValidationException(msg)

        checklist.status = ChecklistStatus.COMPLETED
        checklist.progress_percentage = 100
        checklist.completed_at = datetime.now(UTC)
        checklist.updated_at = datetime.now(UTC)

        updated = await self._uow.checklists.update(checklist)
        logger.info("Checklist completed (checklist_id={})", updated.id)

        # Auto-issue certificate
        existing_certificate = await self._uow.certificates.get_by_checklist_id(checklist_id)
        if not existing_certificate:
            certificate = Certificate(
                cert_uid=str(uuid.uuid4()),
                user_id=updated.user_id,
                checklist_id=updated.id,
                hr_id=updated.hr_id,
                mentor_id=updated.mentor_id,
            )
            await self._uow.certificates.create(certificate)
            logger.info(
                "Certificate auto-issued (cert_uid={}, checklist_id={}, user_id={})",
                certificate.cert_uid,
                checklist_id,
                updated.user_id,
            )

            # Send notification via notification service
            try:
                # Fetch employee data for notification
                employee_data = await auth_service_client.get_user(updated.user_id, self.auth_token)
                if employee_data:
                    employee_name = (
                        f"{employee_data.get('first_name', '')} {employee_data.get('last_name', '')}".strip()
                    )
                    # Fetch template name
                    template = await self._uow.templates.get_by_id(updated.template_id)
                    template_name = template.name if template else "Onboarding"

                    await notification_service_client.send_notification(
                        user_id=updated.user_id,
                        notification_type="certificate_issued",
                        channel="telegram",
                        recipient_telegram_id=employee_data.get("telegram_id"),
                        data={
                            "employee_name": employee_name,
                            "program_name": template_name,
                            "cert_uid": certificate.cert_uid,
                        },
                        auth_token=self.auth_token,
                    )
                    logger.info(
                        "Certificate notification sent (user_id={}, cert_uid={})", updated.user_id, certificate.cert_uid
                    )
            except Exception as e:
                logger.error("Failed to send certificate notification: %s", e)

        return updated

    async def get_checklist_progress(self, checklist_id: int) -> dict[str, Any]:
        """Get detailed progress information for checklist."""
        await self.get_checklist(checklist_id)
        return await self._uow.checklists.get_progress(checklist_id)

    async def get_checklist_stats(
        self,
        user_id: int | None = None,
        department_id: int | None = None,
    ) -> ChecklistStats:
        """Get checklist statistics."""
        stats = await self._uow.checklists.get_statistics(user_id=user_id, department_id=department_id)
        return ChecklistStats(**stats)

    async def get_monthly_stats(self, months: int = 6) -> list[dict[str, Any]]:
        """Get monthly statistics."""
        return await self._uow.checklists.get_monthly_stats(months)

    async def get_completion_time_distribution(self) -> list[dict[str, Any]]:
        """Get completion time distribution."""
        return await self._uow.checklists.get_completion_time_distribution()

    async def auto_create_checklists(
        self,
        user_id: int,
        employee_id: str,
        department_id: int | None,
        position: str | None,
        mentor_id: int | None,
    ) -> list[Checklist]:
        """
        Auto-create checklists for a user from matching templates.

        Finds all ACTIVE templates matching the user's department and position,
        then creates a checklist from each template that the user doesn't already have.
        """
        logger.info(
            "Auto-create checklists started (user_id={}, department_id={}, position={}, mentor_id={})",
            user_id,
            department_id,
            position,
            mentor_id,
        )
        matching_templates = list(await self._uow.templates.find_matching(department_id, position))
        if not matching_templates:
            logger.info("Auto-create checklists: no matching templates (user_id={})", user_id)
            return []

        created_checklists: list[Checklist] = []

        for template in matching_templates:
            existing = await self._uow.checklists.get_by_user_and_template(user_id, template.id)
            if existing:
                logger.debug(
                    "Auto-create skip: checklist already exists (user_id={}, template_id={})",
                    user_id,
                    template.id,
                )
                continue

            start_date = datetime.now(UTC)
            due_date = start_date + timedelta(days=template.duration_days)

            checklist = Checklist(
                user_id=user_id,
                employee_id=employee_id,
                template_id=template.id,
                start_date=start_date,
                due_date=due_date,
                mentor_id=mentor_id,
                status=ChecklistStatus.IN_PROGRESS,
                total_tasks=0,
            )

            checklist = await self._uow.checklists.create(checklist)

            task_templates = list(await self._uow.task_templates.find_by_template(template.id))

            tasks: list[Task] = []
            for _idx, task_template in enumerate(task_templates):
                task_due_date = start_date + timedelta(days=task_template.due_days)
                task_due_date = min(task_due_date, due_date)

                assignee_id = None
                if task_template.auto_assign and task_template.assignee_role:
                    if task_template.assignee_role == "MENTOR" and checklist.mentor_id:
                        assignee_id = checklist.mentor_id
                    elif task_template.assignee_role == "HR" and checklist.hr_id:
                        assignee_id = checklist.hr_id

                task = Task(
                    checklist_id=cast("int", checklist.id),
                    template_task_id=cast("int", task_template.id),
                    title=task_template.title,
                    description=task_template.description,
                    category=task_template.category,
                    order=task_template.order,
                    due_date=task_due_date,
                    assignee_id=assignee_id,
                    assignee_role=task_template.assignee_role or template.default_assignee_role,
                    depends_on=task_template.depends_on.copy() if task_template.depends_on else [],
                    blocks=[],
                )
                tasks.append(task)

            task_map = {task.template_task_id: task for task in tasks if task.template_task_id}
            for task in tasks:
                if task.depends_on:
                    for dep_id in task.depends_on:
                        if dep_id in task_map:
                            if task.template_task_id:
                                task_map[dep_id].blocks.append(task.template_task_id)

            for task in tasks:
                await self._uow.tasks.create(task)

            checklist.total_tasks = len(tasks)
            checklist = await self._uow.checklists.update(checklist)
            created_checklists.append(checklist)
            logger.info(
                "Auto-create: checklist created (checklist_id={}, user_id={}, template_id={}, total_tasks={})",
                checklist.id,
                user_id,
                template.id,
                checklist.total_tasks,
            )

        logger.info(
            "Auto-create checklists finished (user_id={}, created_count={})",
            user_id,
            len(created_checklists),
        )
        return created_checklists
