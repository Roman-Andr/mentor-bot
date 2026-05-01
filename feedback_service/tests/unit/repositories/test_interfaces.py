"""Tests for repository interfaces to cover NotImplementedError lines."""

from datetime import datetime

import pytest
from feedback_service.models import Comment, ExperienceRating, PulseSurvey
from feedback_service.repositories.interfaces import (
    BaseRepository,
    ICommentRepository,
    IExperienceRatingRepository,
    IPulseSurveyRepository,
)


class TestBaseRepositoryInterface:
    """Tests for BaseRepository abstract interface methods."""

    async def test_get_by_id_raises_not_implemented(self) -> None:
        """Test BaseRepository.get_by_id raises NotImplementedError."""

        # Create a concrete class to test the interface
        class ConcreteRepo(BaseRepository[dict, int]):
            async def get_by_id(self, entity_id: int) -> dict | None:
                return await super().get_by_id(entity_id)

            async def get_all(self, *, skip: int = 0, limit: int = 100) -> list[dict]:
                return []

            async def create(self, entity: dict) -> dict:
                return entity

            async def update(self, entity: dict) -> dict:
                return entity

            async def delete(self, entity_id: int) -> bool:
                return True

        repo = ConcreteRepo()

        with pytest.raises(NotImplementedError):
            await repo.get_by_id(1)

    async def test_get_all_raises_not_implemented(self) -> None:
        """Test BaseRepository.get_all raises NotImplementedError."""

        class ConcreteRepo(BaseRepository[dict, int]):
            async def get_by_id(self, entity_id: int) -> dict | None:
                return {}

            async def get_all(self, *, skip: int = 0, limit: int = 100) -> list[dict]:
                return await super().get_all(skip=skip, limit=limit)

            async def create(self, entity: dict) -> dict:
                return entity

            async def update(self, entity: dict) -> dict:
                return entity

            async def delete(self, entity_id: int) -> bool:
                return True

        repo = ConcreteRepo()

        with pytest.raises(NotImplementedError):
            await repo.get_all()

    async def test_create_raises_not_implemented(self) -> None:
        """Test BaseRepository.create raises NotImplementedError."""

        class ConcreteRepo(BaseRepository[dict, int]):
            async def get_by_id(self, entity_id: int) -> dict | None:
                return {}

            async def get_all(self, *, skip: int = 0, limit: int = 100) -> list[dict]:
                return []

            async def create(self, entity: dict) -> dict:
                return await super().create(entity)

            async def update(self, entity: dict) -> dict:
                return entity

            async def delete(self, entity_id: int) -> bool:
                return True

        repo = ConcreteRepo()

        with pytest.raises(NotImplementedError):
            await repo.create({})

    async def test_update_raises_not_implemented(self) -> None:
        """Test BaseRepository.update raises NotImplementedError."""

        class ConcreteRepo(BaseRepository[dict, int]):
            async def get_by_id(self, entity_id: int) -> dict | None:
                return {}

            async def get_all(self, *, skip: int = 0, limit: int = 100) -> list[dict]:
                return []

            async def create(self, entity: dict) -> dict:
                return entity

            async def update(self, entity: dict) -> dict:
                return await super().update(entity)

            async def delete(self, entity_id: int) -> bool:
                return True

        repo = ConcreteRepo()

        with pytest.raises(NotImplementedError):
            await repo.update({})

    async def test_delete_raises_not_implemented(self) -> None:
        """Test BaseRepository.delete raises NotImplementedError."""

        class ConcreteRepo(BaseRepository[dict, int]):
            async def get_by_id(self, entity_id: int) -> dict | None:
                return {}

            async def get_all(self, *, skip: int = 0, limit: int = 100) -> list[dict]:
                return []

            async def create(self, entity: dict) -> dict:
                return entity

            async def update(self, entity: dict) -> dict:
                return entity

            async def delete(self, entity_id: int) -> bool:
                return await super().delete(entity_id)

        repo = ConcreteRepo()

        with pytest.raises(NotImplementedError):
            await repo.delete(1)


class TestIPulseSurveyRepository:
    """Tests for IPulseSurveyRepository interface methods."""

    async def test_find_by_user_raises_not_implemented(self) -> None:
        """Test IPulseSurveyRepository.find_by_user raises NotImplementedError."""

        # Create a minimal concrete implementation that only implements base methods
        # but calls super() for find_by_user
        class TestRepo(IPulseSurveyRepository):
            async def get_by_id(self, entity_id: int) -> PulseSurvey | None:
                return None

            async def get_all(self, *, skip: int = 0, limit: int = 100) -> list[PulseSurvey]:
                return []

            async def create(self, entity: PulseSurvey) -> PulseSurvey:
                return entity

            async def update(self, entity: PulseSurvey) -> PulseSurvey:
                return entity

            async def delete(self, entity_id: int) -> bool:
                return True

            async def find_by_user(self, user_id: int, skip: int = 0, limit: int = 100) -> list[PulseSurvey]:
                return await super().find_by_user(user_id, skip, limit)

            async def get_by_user(
                self, user_id: int | None, from_date: datetime | None, to_date: datetime | None, skip: int, limit: int
            ) -> tuple[list[PulseSurvey], int]:
                raise NotImplementedError

            async def get_stats(
                self, user_id: int | None, from_date: datetime | None, to_date: datetime | None
            ) -> dict:
                raise NotImplementedError

            async def get_rating_distribution(
                self, user_id: int | None, from_date: datetime | None, to_date: datetime | None
            ) -> dict[int, int]:
                raise NotImplementedError

            async def get_anonymity_stats(
                self, department_id: int | None, from_date: datetime | None, to_date: datetime | None
            ) -> dict:
                raise NotImplementedError

        repo = TestRepo()

        with pytest.raises(NotImplementedError):
            await repo.find_by_user(1)


class TestIExperienceRatingRepository:
    """Tests for IExperienceRatingRepository interface methods."""

    async def test_find_by_user_raises_not_implemented(self) -> None:
        """Test IExperienceRatingRepository.find_by_user raises NotImplementedError."""

        class TestRepo(IExperienceRatingRepository):
            async def get_by_id(self, entity_id: int) -> ExperienceRating | None:
                return None

            async def get_all(self, *, skip: int = 0, limit: int = 100) -> list[ExperienceRating]:
                return []

            async def create(self, entity: ExperienceRating) -> ExperienceRating:
                return entity

            async def update(self, entity: ExperienceRating) -> ExperienceRating:
                return entity

            async def delete(self, entity_id: int) -> bool:
                return True

            async def find_by_user(self, user_id: int, skip: int = 0, limit: int = 100) -> list[ExperienceRating]:
                return await super().find_by_user(user_id, skip, limit)

            async def get_by_user(
                self,
                user_id: int | None,
                from_date: datetime | None,
                to_date: datetime | None,
                min_rating: int | None,
                max_rating: int | None,
                skip: int,
                limit: int,
            ) -> tuple[list[ExperienceRating], int]:
                raise NotImplementedError

            async def get_stats(
                self, user_id: int | None, from_date: datetime | None, to_date: datetime | None
            ) -> dict:
                raise NotImplementedError

            async def get_rating_distribution(
                self, user_id: int | None, from_date: datetime | None, to_date: datetime | None
            ) -> dict[int, int]:
                raise NotImplementedError

            async def get_anonymity_stats(
                self, department_id: int | None, from_date: datetime | None, to_date: datetime | None
            ) -> dict:
                raise NotImplementedError

        repo = TestRepo()

        with pytest.raises(NotImplementedError):
            await repo.find_by_user(1)

    async def test_get_by_user_raises_not_implemented(self) -> None:
        """Test IExperienceRatingRepository.get_by_user raises NotImplementedError."""

        class TestRepo(IExperienceRatingRepository):
            async def get_by_id(self, entity_id: int) -> ExperienceRating | None:
                return None

            async def get_all(self, *, skip: int = 0, limit: int = 100) -> list[ExperienceRating]:
                return []

            async def create(self, entity: ExperienceRating) -> ExperienceRating:
                return entity

            async def update(self, entity: ExperienceRating) -> ExperienceRating:
                return entity

            async def delete(self, entity_id: int) -> bool:
                return True

            async def find_by_user(self, user_id: int, skip: int = 0, limit: int = 100) -> list[ExperienceRating]:
                return []

            async def get_by_user(
                self,
                user_id: int | None,
                from_date: datetime | None,
                to_date: datetime | None,
                min_rating: int | None,
                max_rating: int | None,
                skip: int,
                limit: int,
            ) -> tuple[list[ExperienceRating], int]:
                return await super().get_by_user(user_id, from_date, to_date, min_rating, max_rating, skip, limit)

            async def get_stats(
                self, user_id: int | None, from_date: datetime | None, to_date: datetime | None
            ) -> dict:
                raise NotImplementedError

            async def get_rating_distribution(
                self, user_id: int | None, from_date: datetime | None, to_date: datetime | None
            ) -> dict[int, int]:
                raise NotImplementedError

            async def get_anonymity_stats(
                self, department_id: int | None, from_date: datetime | None, to_date: datetime | None
            ) -> dict:
                raise NotImplementedError

        repo = TestRepo()

        with pytest.raises(NotImplementedError):
            await repo.get_by_user(None, None, None, None, None, 0, 50)

    async def test_get_stats_raises_not_implemented(self) -> None:
        """Test IExperienceRatingRepository.get_stats raises NotImplementedError."""

        class TestRepo(IExperienceRatingRepository):
            async def get_by_id(self, entity_id: int) -> ExperienceRating | None:
                return None

            async def get_all(self, *, skip: int = 0, limit: int = 100) -> list[ExperienceRating]:
                return []

            async def create(self, entity: ExperienceRating) -> ExperienceRating:
                return entity

            async def update(self, entity: ExperienceRating) -> ExperienceRating:
                return entity

            async def delete(self, entity_id: int) -> bool:
                return True

            async def find_by_user(self, user_id: int, skip: int = 0, limit: int = 100) -> list[ExperienceRating]:
                return []

            async def get_by_user(
                self,
                user_id: int | None,
                from_date: datetime | None,
                to_date: datetime | None,
                min_rating: int | None,
                max_rating: int | None,
                skip: int,
                limit: int,
            ) -> tuple[list[ExperienceRating], int]:
                raise NotImplementedError

            async def get_stats(
                self, user_id: int | None, from_date: datetime | None, to_date: datetime | None
            ) -> dict:
                return await super().get_stats(user_id, from_date, to_date)

            async def get_rating_distribution(
                self, user_id: int | None, from_date: datetime | None, to_date: datetime | None
            ) -> dict[int, int]:
                raise NotImplementedError

            async def get_anonymity_stats(
                self, department_id: int | None, from_date: datetime | None, to_date: datetime | None
            ) -> dict:
                raise NotImplementedError

        repo = TestRepo()

        with pytest.raises(NotImplementedError):
            await repo.get_stats(None, None, None)

    async def test_get_rating_distribution_raises_not_implemented(self) -> None:
        """Test IExperienceRatingRepository.get_rating_distribution raises NotImplementedError."""

        class TestRepo(IExperienceRatingRepository):
            async def get_by_id(self, entity_id: int) -> ExperienceRating | None:
                return None

            async def get_all(self, *, skip: int = 0, limit: int = 100) -> list[ExperienceRating]:
                return []

            async def create(self, entity: ExperienceRating) -> ExperienceRating:
                return entity

            async def update(self, entity: ExperienceRating) -> ExperienceRating:
                return entity

            async def delete(self, entity_id: int) -> bool:
                return True

            async def find_by_user(self, user_id: int, skip: int = 0, limit: int = 100) -> list[ExperienceRating]:
                return []

            async def get_by_user(
                self,
                user_id: int | None,
                from_date: datetime | None,
                to_date: datetime | None,
                min_rating: int | None,
                max_rating: int | None,
                skip: int,
                limit: int,
            ) -> tuple[list[ExperienceRating], int]:
                raise NotImplementedError

            async def get_stats(
                self, user_id: int | None, from_date: datetime | None, to_date: datetime | None
            ) -> dict:
                raise NotImplementedError

            async def get_rating_distribution(
                self, user_id: int | None, from_date: datetime | None, to_date: datetime | None
            ) -> dict[int, int]:
                return await super().get_rating_distribution(user_id, from_date, to_date)

            async def get_anonymity_stats(
                self, department_id: int | None, from_date: datetime | None, to_date: datetime | None
            ) -> dict:
                raise NotImplementedError

        repo = TestRepo()

        with pytest.raises(NotImplementedError):
            await repo.get_rating_distribution(None, None, None)


class TestIPulseSurveyRepositoryAdditional:
    """Additional tests for IPulseSurveyRepository."""

    async def test_get_by_user_raises_not_implemented(self) -> None:
        """Test IPulseSurveyRepository.get_by_user raises NotImplementedError."""

        class TestRepo(IPulseSurveyRepository):
            async def get_by_id(self, entity_id: int) -> PulseSurvey | None:
                return None

            async def get_all(self, *, skip: int = 0, limit: int = 100) -> list[PulseSurvey]:
                return []

            async def create(self, entity: PulseSurvey) -> PulseSurvey:
                return entity

            async def update(self, entity: PulseSurvey) -> PulseSurvey:
                return entity

            async def delete(self, entity_id: int) -> bool:
                return True

            async def find_by_user(self, user_id: int, skip: int = 0, limit: int = 100) -> list[PulseSurvey]:
                return []

            async def get_by_user(
                self, user_id: int | None, from_date: datetime | None, to_date: datetime | None, skip: int, limit: int
            ) -> tuple[list[PulseSurvey], int]:
                return await super().get_by_user(user_id, from_date, to_date, None, skip, limit)

            async def get_stats(
                self, user_id: int | None, from_date: datetime | None, to_date: datetime | None
            ) -> dict:
                raise NotImplementedError

            async def get_rating_distribution(
                self, user_id: int | None, from_date: datetime | None, to_date: datetime | None
            ) -> dict[int, int]:
                raise NotImplementedError

            async def get_anonymity_stats(
                self, department_id: int | None, from_date: datetime | None, to_date: datetime | None
            ) -> dict:
                raise NotImplementedError

        repo = TestRepo()

        with pytest.raises(NotImplementedError):
            await repo.get_by_user(None, None, None, 0, 50)

    async def test_get_stats_raises_not_implemented(self) -> None:
        """Test IPulseSurveyRepository.get_stats raises NotImplementedError."""

        class TestRepo(IPulseSurveyRepository):
            async def get_by_id(self, entity_id: int) -> PulseSurvey | None:
                return None

            async def get_all(self, *, skip: int = 0, limit: int = 100) -> list[PulseSurvey]:
                return []

            async def create(self, entity: PulseSurvey) -> PulseSurvey:
                return entity

            async def update(self, entity: PulseSurvey) -> PulseSurvey:
                return entity

            async def delete(self, entity_id: int) -> bool:
                return True

            async def find_by_user(self, user_id: int, skip: int = 0, limit: int = 100) -> list[PulseSurvey]:
                return []

            async def get_by_user(
                self, user_id: int | None, from_date: datetime | None, to_date: datetime | None, skip: int, limit: int
            ) -> tuple[list[PulseSurvey], int]:
                raise NotImplementedError

            async def get_stats(
                self, user_id: int | None, from_date: datetime | None, to_date: datetime | None
            ) -> dict:
                return await super().get_stats(user_id, from_date, to_date)

            async def get_rating_distribution(
                self, user_id: int | None, from_date: datetime | None, to_date: datetime | None
            ) -> dict[int, int]:
                raise NotImplementedError

            async def get_anonymity_stats(
                self, department_id: int | None, from_date: datetime | None, to_date: datetime | None
            ) -> dict:
                raise NotImplementedError

        repo = TestRepo()

        with pytest.raises(NotImplementedError):
            await repo.get_stats(None, None, None)

    async def test_get_rating_distribution_raises_not_implemented(self) -> None:
        """Test IPulseSurveyRepository.get_rating_distribution raises NotImplementedError."""

        class TestRepo(IPulseSurveyRepository):
            async def get_by_id(self, entity_id: int) -> PulseSurvey | None:
                return None

            async def get_all(self, *, skip: int = 0, limit: int = 100) -> list[PulseSurvey]:
                return []

            async def create(self, entity: PulseSurvey) -> PulseSurvey:
                return entity

            async def update(self, entity: PulseSurvey) -> PulseSurvey:
                return entity

            async def delete(self, entity_id: int) -> bool:
                return True

            async def find_by_user(self, user_id: int, skip: int = 0, limit: int = 100) -> list[PulseSurvey]:
                return []

            async def get_by_user(
                self, user_id: int | None, from_date: datetime | None, to_date: datetime | None, skip: int, limit: int
            ) -> tuple[list[PulseSurvey], int]:
                raise NotImplementedError

            async def get_stats(
                self, user_id: int | None, from_date: datetime | None, to_date: datetime | None
            ) -> dict:
                raise NotImplementedError

            async def get_rating_distribution(
                self, user_id: int | None, from_date: datetime | None, to_date: datetime | None
            ) -> dict[int, int]:
                return await super().get_rating_distribution(user_id, from_date, to_date)

            async def get_anonymity_stats(
                self, department_id: int | None, from_date: datetime | None, to_date: datetime | None
            ) -> dict:
                raise NotImplementedError

        repo = TestRepo()

        with pytest.raises(NotImplementedError):
            await repo.get_rating_distribution(None, None, None)


class TestICommentRepository:
    """Tests for ICommentRepository interface methods."""

    async def test_find_by_user_raises_not_implemented(self) -> None:
        """Test ICommentRepository.find_by_user raises NotImplementedError."""

        class TestRepo(ICommentRepository):
            async def get_by_id(self, entity_id: int) -> Comment | None:
                return None

            async def get_all(self, *, skip: int = 0, limit: int = 100) -> list[Comment]:
                return []

            async def create(self, entity: Comment) -> Comment:
                return entity

            async def update(self, entity: Comment) -> Comment:
                return entity

            async def delete(self, entity_id: int) -> bool:
                return True

            async def find_by_user(self, user_id: int, skip: int = 0, limit: int = 100) -> list[Comment]:
                return await super().find_by_user(user_id, skip, limit)

            async def get_by_user(
                self,
                user_id: int | None,
                from_date: datetime | None,
                to_date: datetime | None,
                search: str | None,
                has_reply: bool | None,
                skip: int,
                limit: int,
            ) -> tuple[list[Comment], int]:
                raise NotImplementedError

            async def add_reply(self, comment_id: int, reply: str, replied_by: int) -> Comment | None:
                raise NotImplementedError

            async def get_anonymity_stats(
                self, department_id: int | None, from_date: datetime | None, to_date: datetime | None
            ) -> dict:
                raise NotImplementedError

            async def get_reply_eligible_comments(
                self,
                department_id: int | None,
                from_date: datetime | None,
                to_date: datetime | None,
                skip: int,
                limit: int,
            ) -> tuple[list[Comment], int]:
                raise NotImplementedError

        repo = TestRepo()

        with pytest.raises(NotImplementedError):
            await repo.find_by_user(1)

    async def test_get_by_user_raises_not_implemented(self) -> None:
        """Test ICommentRepository.get_by_user raises NotImplementedError."""

        class TestRepo(ICommentRepository):
            async def get_by_id(self, entity_id: int) -> Comment | None:
                return None

            async def get_all(self, *, skip: int = 0, limit: int = 100) -> list[Comment]:
                return []

            async def create(self, entity: Comment) -> Comment:
                return entity

            async def update(self, entity: Comment) -> Comment:
                return entity

            async def delete(self, entity_id: int) -> bool:
                return True

            async def find_by_user(self, user_id: int, skip: int = 0, limit: int = 100) -> list[Comment]:
                return []

            async def get_by_user(
                self,
                user_id: int | None,
                from_date: datetime | None,
                to_date: datetime | None,
                search: str | None,
                has_reply: bool | None,
                skip: int,
                limit: int,
            ) -> tuple[list[Comment], int]:
                return await super().get_by_user(user_id, from_date, to_date, search, has_reply, skip, limit)

            async def add_reply(self, comment_id: int, reply: str, replied_by: int) -> Comment | None:
                raise NotImplementedError

            async def get_anonymity_stats(
                self, department_id: int | None, from_date: datetime | None, to_date: datetime | None
            ) -> dict:
                raise NotImplementedError

            async def get_reply_eligible_comments(
                self,
                department_id: int | None,
                from_date: datetime | None,
                to_date: datetime | None,
                skip: int,
                limit: int,
            ) -> tuple[list[Comment], int]:
                raise NotImplementedError

        repo = TestRepo()

        with pytest.raises(NotImplementedError):
            await repo.get_by_user(None, None, None, None, None, 0, 50)

    async def test_add_reply_raises_not_implemented(self) -> None:
        """Test ICommentRepository.add_reply raises NotImplementedError."""

        class TestRepo(ICommentRepository):
            async def get_by_id(self, entity_id: int) -> Comment | None:
                return None

            async def get_all(self, *, skip: int = 0, limit: int = 100) -> list[Comment]:
                return []

            async def create(self, entity: Comment) -> Comment:
                return entity

            async def update(self, entity: Comment) -> Comment:
                return entity

            async def delete(self, entity_id: int) -> bool:
                return True

            async def find_by_user(self, user_id: int, skip: int = 0, limit: int = 100) -> list[Comment]:
                return []

            async def get_by_user(
                self,
                user_id: int | None,
                from_date: datetime | None,
                to_date: datetime | None,
                search: str | None,
                has_reply: bool | None,
                skip: int,
                limit: int,
            ) -> tuple[list[Comment], int]:
                raise NotImplementedError

            async def add_reply(self, comment_id: int, reply: str, replied_by: int) -> Comment | None:
                return await super().add_reply(comment_id, reply, replied_by)

            async def get_anonymity_stats(
                self, department_id: int | None, from_date: datetime | None, to_date: datetime | None
            ) -> dict:
                raise NotImplementedError

            async def get_reply_eligible_comments(
                self,
                department_id: int | None,
                from_date: datetime | None,
                to_date: datetime | None,
                skip: int,
                limit: int,
            ) -> tuple[list[Comment], int]:
                raise NotImplementedError

        repo = TestRepo()

        with pytest.raises(NotImplementedError):
            await repo.add_reply(1, "Reply", 2)

    async def test_get_anonymity_stats_raises_not_implemented(self) -> None:
        """Test ICommentRepository.get_anonymity_stats raises NotImplementedError."""

        class TestRepo(ICommentRepository):
            async def get_by_id(self, entity_id: int) -> Comment | None:
                return None

            async def get_all(self, *, skip: int = 0, limit: int = 100) -> list[Comment]:
                return []

            async def create(self, entity: Comment) -> Comment:
                return entity

            async def update(self, entity: Comment) -> Comment:
                return entity

            async def delete(self, entity_id: int) -> bool:
                return True

            async def find_by_user(self, user_id: int, skip: int = 0, limit: int = 100) -> list[Comment]:
                return []

            async def get_by_user(
                self,
                user_id: int | None,
                from_date: datetime | None,
                to_date: datetime | None,
                search: str | None,
                has_reply: bool | None,
                skip: int,
                limit: int,
            ) -> tuple[list[Comment], int]:
                raise NotImplementedError

            async def add_reply(self, comment_id: int, reply: str, replied_by: int) -> Comment | None:
                raise NotImplementedError

            async def get_anonymity_stats(
                self, department_id: int | None, from_date: datetime | None, to_date: datetime | None
            ) -> dict:
                return await super().get_anonymity_stats(department_id, from_date, to_date)

            async def get_reply_eligible_comments(
                self,
                department_id: int | None,
                from_date: datetime | None,
                to_date: datetime | None,
                skip: int,
                limit: int,
            ) -> tuple[list[Comment], int]:
                raise NotImplementedError

        repo = TestRepo()

        with pytest.raises(NotImplementedError):
            await repo.get_anonymity_stats(None, None, None)

    async def test_get_reply_eligible_comments_raises_not_implemented(self) -> None:
        """Test ICommentRepository.get_reply_eligible_comments raises NotImplementedError."""

        class TestRepo(ICommentRepository):
            async def get_by_id(self, entity_id: int) -> Comment | None:
                return None

            async def get_all(self, *, skip: int = 0, limit: int = 100) -> list[Comment]:
                return []

            async def create(self, entity: Comment) -> Comment:
                return entity

            async def update(self, entity: Comment) -> Comment:
                return entity

            async def delete(self, entity_id: int) -> bool:
                return True

            async def find_by_user(self, user_id: int, skip: int = 0, limit: int = 100) -> list[Comment]:
                return []

            async def get_by_user(
                self,
                user_id: int | None,
                from_date: datetime | None,
                to_date: datetime | None,
                search: str | None,
                has_reply: bool | None,
                skip: int,
                limit: int,
            ) -> tuple[list[Comment], int]:
                raise NotImplementedError

            async def add_reply(self, comment_id: int, reply: str, replied_by: int) -> Comment | None:
                raise NotImplementedError

            async def get_anonymity_stats(
                self, department_id: int | None, from_date: datetime | None, to_date: datetime | None
            ) -> dict:
                raise NotImplementedError

            async def get_reply_eligible_comments(
                self,
                department_id: int | None,
                from_date: datetime | None,
                to_date: datetime | None,
                skip: int,
                limit: int,
            ) -> tuple[list[Comment], int]:
                return await super().get_reply_eligible_comments(department_id, from_date, to_date, skip, limit)

        repo = TestRepo()

        with pytest.raises(NotImplementedError):
            await repo.get_reply_eligible_comments(None, None, None, 0, 50)


class TestIPulseSurveyRepositoryGetAnonymityStats:
    """Tests for IPulseSurveyRepository.get_anonymity_stats."""

    async def test_get_anonymity_stats_raises_not_implemented(self) -> None:
        """Test IPulseSurveyRepository.get_anonymity_stats raises NotImplementedError."""

        class TestRepo(IPulseSurveyRepository):
            async def get_by_id(self, entity_id: int) -> PulseSurvey | None:
                return None

            async def get_all(self, *, skip: int = 0, limit: int = 100) -> list[PulseSurvey]:
                return []

            async def create(self, entity: PulseSurvey) -> PulseSurvey:
                return entity

            async def update(self, entity: PulseSurvey) -> PulseSurvey:
                return entity

            async def delete(self, entity_id: int) -> bool:
                return True

            async def find_by_user(self, user_id: int, skip: int = 0, limit: int = 100) -> list[PulseSurvey]:
                return []

            async def get_by_user(
                self, user_id: int | None, from_date: datetime | None, to_date: datetime | None, skip: int, limit: int
            ) -> tuple[list[PulseSurvey], int]:
                raise NotImplementedError

            async def get_stats(
                self, user_id: int | None, from_date: datetime | None, to_date: datetime | None
            ) -> dict:
                raise NotImplementedError

            async def get_rating_distribution(
                self, user_id: int | None, from_date: datetime | None, to_date: datetime | None
            ) -> dict[int, int]:
                raise NotImplementedError

            async def get_anonymity_stats(
                self, department_id: int | None, from_date: datetime | None, to_date: datetime | None
            ) -> dict:
                return await super().get_anonymity_stats(department_id, from_date, to_date)

        repo = TestRepo()

        with pytest.raises(NotImplementedError):
            await repo.get_anonymity_stats(None, None, None)


class TestIExperienceRatingRepositoryGetAnonymityStats:
    """Tests for IExperienceRatingRepository.get_anonymity_stats."""

    async def test_get_anonymity_stats_raises_not_implemented(self) -> None:
        """Test IExperienceRatingRepository.get_anonymity_stats raises NotImplementedError."""

        class TestRepo(IExperienceRatingRepository):
            async def get_by_id(self, entity_id: int) -> ExperienceRating | None:
                return None

            async def get_all(self, *, skip: int = 0, limit: int = 100) -> list[ExperienceRating]:
                return []

            async def create(self, entity: ExperienceRating) -> ExperienceRating:
                return entity

            async def update(self, entity: ExperienceRating) -> ExperienceRating:
                return entity

            async def delete(self, entity_id: int) -> bool:
                return True

            async def find_by_user(self, user_id: int, skip: int = 0, limit: int = 100) -> list[ExperienceRating]:
                return []

            async def get_by_user(
                self,
                user_id: int | None,
                from_date: datetime | None,
                to_date: datetime | None,
                min_rating: int | None,
                max_rating: int | None,
                skip: int,
                limit: int,
            ) -> tuple[list[ExperienceRating], int]:
                raise NotImplementedError

            async def get_stats(
                self, user_id: int | None, from_date: datetime | None, to_date: datetime | None
            ) -> dict:
                raise NotImplementedError

            async def get_rating_distribution(
                self, user_id: int | None, from_date: datetime | None, to_date: datetime | None
            ) -> dict[int, int]:
                raise NotImplementedError

            async def get_anonymity_stats(
                self, department_id: int | None, from_date: datetime | None, to_date: datetime | None
            ) -> dict:
                return await super().get_anonymity_stats(department_id, from_date, to_date)

        repo = TestRepo()

        with pytest.raises(NotImplementedError):
            await repo.get_anonymity_stats(None, None, None)
