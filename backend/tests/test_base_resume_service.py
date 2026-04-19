from __future__ import annotations

from typing import Optional

import psycopg
import pytest

from app.db.base_resumes import BaseResumeRecord
from app.services.base_resumes import BaseResumeService


class StubBaseResumeRepository:
    def __init__(
        self,
        *,
        existing: bool = True,
        referenced: bool = False,
        delete_result: bool = True,
        delete_error: Optional[Exception] = None,
    ) -> None:
        self.existing = existing
        self.referenced = referenced
        self.delete_result = delete_result
        self.delete_error = delete_error
        self.delete_calls = 0

    def fetch_resume(self, user_id: str, resume_id: str) -> Optional[BaseResumeRecord]:
        if not self.existing:
            return None
        return BaseResumeRecord(
            id=resume_id,
            name="Backend Resume",
            user_id=user_id,
            content_md="# Resume",
            created_at="2026-04-07T12:00:00Z",
            updated_at="2026-04-07T12:00:00Z",
        )

    def is_referenced(self, resume_id: str, user_id: str) -> bool:
        return self.referenced

    def delete_resume(self, resume_id: str, user_id: str) -> bool:
        self.delete_calls += 1
        if self.delete_error is not None:
            raise self.delete_error
        return self.delete_result


class StubProfileRepository:
    def fetch_default_resume_id(self, user_id: str) -> Optional[str]:
        return None

    def update_default_resume(self, user_id: str, resume_id: Optional[str]) -> None:
        return None


def test_delete_resume_blocks_referenced_resume_without_force():
    repository = StubBaseResumeRepository(referenced=True)
    service = BaseResumeService(
        repo=repository,  # type: ignore[arg-type]
        profile_repo=StubProfileRepository(),  # type: ignore[arg-type]
    )

    with pytest.raises(ValueError, match="Use force=true to delete anyway."):
        service.delete_resume(user_id="user-1", resume_id="resume-1", force=False)

    assert repository.delete_calls == 0


def test_delete_resume_allows_referenced_resume_with_force():
    repository = StubBaseResumeRepository(referenced=True)
    service = BaseResumeService(
        repo=repository,  # type: ignore[arg-type]
        profile_repo=StubProfileRepository(),  # type: ignore[arg-type]
    )

    service.delete_resume(user_id="user-1", resume_id="resume-1", force=True)

    assert repository.delete_calls == 1


def test_delete_resume_raises_not_found_when_record_missing():
    repository = StubBaseResumeRepository(existing=False)
    service = BaseResumeService(
        repo=repository,  # type: ignore[arg-type]
        profile_repo=StubProfileRepository(),  # type: ignore[arg-type]
    )

    with pytest.raises(LookupError, match="Base resume not found."):
        service.delete_resume(user_id="user-1", resume_id="resume-1", force=True)


def test_delete_resume_maps_foreign_key_violation_to_permission_error():
    repository = StubBaseResumeRepository(
        referenced=True,
        delete_error=psycopg.errors.ForeignKeyViolation("fk violation"),
    )
    service = BaseResumeService(
        repo=repository,  # type: ignore[arg-type]
        profile_repo=StubProfileRepository(),  # type: ignore[arg-type]
    )

    with pytest.raises(PermissionError, match="related records still reference it"):
        service.delete_resume(user_id="user-1", resume_id="resume-1", force=True)
