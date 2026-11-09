from datetime import date

import pytest

from applytrack.models import (
    ALLOWED_TRANSITIONS,
    Application,
    InvalidTransitionError,
    Status,
)


def make_app(**kwargs) -> Application:
    return Application(company="Acme", role="Werkstudent", **kwargs)


def test_new_application_starts_as_planned():
    assert make_app().status is Status.PLANNED


def test_valid_transition_sets_status():
    app = make_app(status=Status.APPLIED)
    app.move_to(Status.INTERVIEW)
    assert app.status is Status.INTERVIEW


def test_planned_cannot_jump_to_offer():
    app = make_app()
    with pytest.raises(InvalidTransitionError):
        app.move_to(Status.OFFER)
    assert app.status is Status.PLANNED


def test_moving_to_applied_sets_applied_on_once():
    app = make_app()
    app.move_to(Status.APPLIED, today=date(2026, 11, 9))
    assert app.applied_on == date(2026, 11, 9)


def test_existing_applied_on_is_kept():
    app = make_app(applied_on=date(2026, 1, 1))
    app.move_to(Status.APPLIED, today=date(2026, 11, 9))
    assert app.applied_on == date(2026, 1, 1)


def test_ghosted_can_return_to_interview():
    app = make_app(status=Status.GHOSTED)
    assert app.can_move_to(Status.INTERVIEW)


@pytest.mark.parametrize("final", [Status.OFFER, Status.REJECTED])
def test_final_states_have_no_exits(final):
    assert ALLOWED_TRANSITIONS[final] == frozenset()
