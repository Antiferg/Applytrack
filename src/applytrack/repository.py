"""SQLite persistence for applications. Contains no business rules."""

from __future__ import annotations

import sqlite3
from datetime import date

from .models import Application, Status

_SCHEMA = """
CREATE TABLE IF NOT EXISTS applications (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    company    TEXT NOT NULL,
    role       TEXT NOT NULL,
    location   TEXT NOT NULL DEFAULT '',
    source     TEXT NOT NULL DEFAULT '',
    status     TEXT NOT NULL,
    applied_on TEXT,
    deadline   TEXT,
    notes      TEXT NOT NULL DEFAULT ''
)
"""


def _to_iso(value: date | None) -> str | None:
    return value.isoformat() if value else None


def _from_iso(value: str | None) -> date | None:
    return date.fromisoformat(value) if value else None


def _row_to_application(row: sqlite3.Row) -> Application:
    return Application(
        id=row["id"],
        company=row["company"],
        role=row["role"],
        location=row["location"],
        source=row["source"],
        status=Status(row["status"]),
        applied_on=_from_iso(row["applied_on"]),
        deadline=_from_iso(row["deadline"]),
        notes=row["notes"],
    )


class SQLiteRepository:
    def __init__(self, path: str = ":memory:") -> None:
        self._conn = sqlite3.connect(path)
        self._conn.row_factory = sqlite3.Row
        self._conn.execute(_SCHEMA)
        self._conn.commit()

    def close(self) -> None:
        self._conn.close()

    def add(self, app: Application) -> Application:
        cur = self._conn.execute(
            "INSERT INTO applications "
            "(company, role, location, source, status, applied_on, deadline, notes) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (
                app.company,
                app.role,
                app.location,
                app.source,
                app.status.value,
                _to_iso(app.applied_on),
                _to_iso(app.deadline),
                app.notes,
            ),
        )
        self._conn.commit()
        app.id = cur.lastrowid
        return app

    def get(self, app_id: int) -> Application | None:
        row = self._conn.execute("SELECT * FROM applications WHERE id = ?", (app_id,)).fetchone()
        return _row_to_application(row) if row else None

    def list(self, status: Status | None = None) -> list[Application]:
        if status is None:
            rows = self._conn.execute("SELECT * FROM applications ORDER BY id").fetchall()
        else:
            rows = self._conn.execute(
                "SELECT * FROM applications WHERE status = ? ORDER BY id", (status.value,)
            ).fetchall()
        return [_row_to_application(r) for r in rows]

    def update(self, app: Application) -> None:
        if app.id is None:
            raise ValueError("Cannot update an application without an id")
        self._conn.execute(
            "UPDATE applications SET company=?, role=?, location=?, source=?, status=?, "
            "applied_on=?, deadline=?, notes=? WHERE id=?",
            (
                app.company,
                app.role,
                app.location,
                app.source,
                app.status.value,
                _to_iso(app.applied_on),
                _to_iso(app.deadline),
                app.notes,
                app.id,
            ),
        )
        self._conn.commit()

    def delete(self, app_id: int) -> bool:
        cur = self._conn.execute("DELETE FROM applications WHERE id = ?", (app_id,))
        self._conn.commit()
        return cur.rowcount > 0
