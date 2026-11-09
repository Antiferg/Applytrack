"""Domain model: applications, statuses and the allowed status transitions."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from enum import Enum


class Status(str, Enum):
    PLANNED = "planned"
    APPLIED = "applied"
    INTERVIEW = "interview"
    OFFER = "offer"
    REJECTED = "rejected"
    GHOSTED = "ghosted"


ALLOWED_TRANSITIONS: dict[Status, frozenset[Status]] = {
    Status.PLANNED: frozenset({Status.APPLIED}),
    Status.APPLIED: frozenset({Status.INTERVIEW, Status.REJECTED, Status.GHOSTED}),
    Status.INTERVIEW: frozenset({Status.OFFER, Status.REJECTED, Status.GHOSTED}),
    # A company that went silent can still reply late.
    Status.GHOSTED: frozenset({Status.INTERVIEW, Status.REJECTED}),
    Status.OFFER: frozenset(),
    Status.REJECTED: frozenset(),
}


class InvalidTransitionError(ValueError):
    """Raised when a status change is not allowed by the workflow."""


@dataclass
class Application:
    company: str
    role: str
    location: str = ""
    source: str = ""
    status: Status = Status.PLANNED
    applied_on: date | None = None
    deadline: date | None = None
    notes: str = ""
    id: int | None = None

    def can_move_to(self, new_status: Status) -> bool:
        return new_status in ALLOWED_TRANSITIONS[self.status]

    def move_to(self, new_status: Status, today: date | None = None) -> None:
        """Change status if the workflow allows it, setting applied_on on first apply."""
        if not self.can_move_to(new_status):
            raise InvalidTransitionError(
                f"Cannot move from '{self.status.value}' to '{new_status.value}'"
            )
        if new_status is Status.APPLIED and self.applied_on is None:
            self.applied_on = today or date.today()
        self.status = new_status
