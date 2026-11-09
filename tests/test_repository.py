from datetime import date

import pytest

from applytrack.models import Application, Status
from applytrack.repository import SQLiteRepository


@pytest.fixture
def repo():
    r = SQLiteRepository(":memory:")
    yield r
    r.close()


def test_add_assigns_id_and_get_roundtrips(repo):
    app = repo.add(
        Application(
            company="Acme",
            role="Werkstudent",
            location="Berlin",
            deadline=date(2026, 12, 1),
            notes="referral",
        )
    )
    assert app.id is not None
    loaded = repo.get(app.id)
    assert loaded == app


def test_get_missing_returns_none(repo):
    assert repo.get(999) is None


def test_list_filters_by_status(repo):
    repo.add(Application(company="A", role="r"))
    repo.add(Application(company="B", role="r", status=Status.APPLIED))
    assert [a.company for a in repo.list()] == ["A", "B"]
    assert [a.company for a in repo.list(status=Status.APPLIED)] == ["B"]


def test_update_persists_changes(repo):
    app = repo.add(Application(company="A", role="r"))
    app.move_to(Status.APPLIED, today=date(2026, 11, 9))
    repo.update(app)
    loaded = repo.get(app.id)
    assert loaded.status is Status.APPLIED
    assert loaded.applied_on == date(2026, 11, 9)


def test_update_without_id_raises(repo):
    with pytest.raises(ValueError):
        repo.update(Application(company="A", role="r"))


def test_delete(repo):
    app = repo.add(Application(company="A", role="r"))
    assert repo.delete(app.id) is True
    assert repo.delete(app.id) is False
    assert repo.get(app.id) is None
