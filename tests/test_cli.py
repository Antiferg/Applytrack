import pytest
from typer.testing import CliRunner

from applytrack.cli import app

runner = CliRunner()


@pytest.fixture(autouse=True)
def temp_db(tmp_path, monkeypatch):
    monkeypatch.setenv("APPLYTRACK_DB", str(tmp_path / "test.db"))


def test_add_and_list():
    result = runner.invoke(app, ["add", "Acme", "Werkstudent", "--deadline", "2026-12-01"])
    assert result.exit_code == 0
    assert "Added application #1" in result.output

    listing = runner.invoke(app, ["list"])
    assert "Acme" in listing.output
    assert "planned" in listing.output
    assert "2026-12-01" in listing.output


def test_list_empty():
    result = runner.invoke(app, ["list"])
    assert "No applications found." in result.output


def test_invalid_deadline_is_rejected():
    result = runner.invoke(app, ["add", "Acme", "Role", "--deadline", "01.12.2026"])
    assert result.exit_code != 0


def test_move_follows_workflow():
    runner.invoke(app, ["add", "Acme", "Role"])
    ok = runner.invoke(app, ["move", "1", "applied"])
    assert ok.exit_code == 0

    bad = runner.invoke(app, ["move", "1", "offer"])
    assert bad.exit_code == 1


def test_list_filter_by_status():
    runner.invoke(app, ["add", "Acme", "Role"])
    runner.invoke(app, ["add", "Beta", "Role"])
    runner.invoke(app, ["move", "2", "applied"])
    result = runner.invoke(app, ["list", "--status", "applied"])
    assert "Beta" in result.output
    assert "Acme" not in result.output


def test_show_and_delete():
    runner.invoke(app, ["add", "Acme", "Role", "--notes", "referral"])
    assert "referral" in runner.invoke(app, ["show", "1"]).output
    assert runner.invoke(app, ["delete", "1"]).exit_code == 0
    assert runner.invoke(app, ["show", "1"]).exit_code == 1
