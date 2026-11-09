"""Command-line interface. A thin layer over the models and the repository."""

from __future__ import annotations

import os
from datetime import date
from pathlib import Path

import typer

from .models import Application, InvalidTransitionError, Status
from .repository import SQLiteRepository

app = typer.Typer(help="Track job applications from the command line.", no_args_is_help=True)


def _db_path() -> str:
    override = os.environ.get("APPLYTRACK_DB")
    if override:
        return override
    default = Path.home() / ".applytrack" / "applytrack.db"
    default.parent.mkdir(parents=True, exist_ok=True)
    return str(default)


def _repo() -> SQLiteRepository:
    return SQLiteRepository(_db_path())


def _parse_date(value: str | None) -> date | None:
    if value is None:
        return None
    try:
        return date.fromisoformat(value)
    except ValueError:
        raise typer.BadParameter(f"'{value}' is not a valid date, use YYYY-MM-DD") from None


def _format_row(a: Application) -> str:
    deadline = a.deadline.isoformat() if a.deadline else "-"
    return f"{a.id:>3}  {a.status.value:<10}  {a.company:<20}  {a.role:<28}  {deadline}"


@app.command()
def add(
    company: str,
    role: str,
    location: str = typer.Option("", help="City or 'Remote'"),
    source: str = typer.Option("", help="Where you found the posting"),
    deadline: str = typer.Option(None, help="Application deadline, YYYY-MM-DD"),
    notes: str = typer.Option("", help="Free-form notes"),
) -> None:
    """Add a new application (starts as 'planned')."""
    repo = _repo()
    created = repo.add(
        Application(
            company=company,
            role=role,
            location=location,
            source=source,
            deadline=_parse_date(deadline),
            notes=notes,
        )
    )
    typer.echo(f"Added application #{created.id}: {company} - {role}")


@app.command("list")
def list_applications(
    status: Status = typer.Option(None, help="Only show this status"),
) -> None:
    """List applications."""
    apps = _repo().list(status=status)
    if not apps:
        typer.echo("No applications found.")
        return
    typer.echo(f"{'ID':>3}  {'STATUS':<10}  {'COMPANY':<20}  {'ROLE':<28}  DEADLINE")
    for a in apps:
        typer.echo(_format_row(a))


@app.command()
def show(app_id: int) -> None:
    """Show all details of one application."""
    a = _repo().get(app_id)
    if a is None:
        typer.echo(f"No application with id {app_id}", err=True)
        raise typer.Exit(code=1)
    typer.echo(f"#{a.id} {a.company} - {a.role}")
    typer.echo(f"  status:     {a.status.value}")
    typer.echo(f"  location:   {a.location or '-'}")
    typer.echo(f"  source:     {a.source or '-'}")
    typer.echo(f"  applied on: {a.applied_on or '-'}")
    typer.echo(f"  deadline:   {a.deadline or '-'}")
    typer.echo(f"  notes:      {a.notes or '-'}")


@app.command()
def move(app_id: int, new_status: Status) -> None:
    """Move an application to a new status, following the workflow."""
    repo = _repo()
    a = repo.get(app_id)
    if a is None:
        typer.echo(f"No application with id {app_id}", err=True)
        raise typer.Exit(code=1)
    try:
        a.move_to(new_status)
    except InvalidTransitionError as exc:
        typer.echo(str(exc), err=True)
        raise typer.Exit(code=1) from None
    repo.update(a)
    typer.echo(f"#{a.id} is now '{a.status.value}'")


@app.command()
def delete(app_id: int) -> None:
    """Delete an application."""
    if not _repo().delete(app_id):
        typer.echo(f"No application with id {app_id}", err=True)
        raise typer.Exit(code=1)
    typer.echo(f"Deleted application #{app_id}")


if __name__ == "__main__":
    app()
