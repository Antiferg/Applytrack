# applytrack

A small command-line tool for tracking job applications: where you applied, what
stage each application is in, and which deadlines are coming up.

I built it while applying for Werkstudent positions in Germany, because a
spreadsheet stops working once you have 30+ applications in different stages.

## Status

Early version (v0.1). The core domain model, SQLite storage and a CLI work.
See [ROADMAP.md](ROADMAP.md) for what is planned next.

## Features

- Add applications with company, role, location, source, deadline and notes
- Status workflow with validated transitions (no jumping from `planned` to `offer`)
- List and filter applications by status
- Local SQLite storage, no server needed

## Status workflow

```
planned -> applied -> interview -> offer
              |           |
              +-> rejected <-+
              +-> ghosted  <-+   (ghosted -> interview is allowed if they reply late)
```

## Install

Requires Python 3.10+.

```bash
git clone <this repo>
cd applytrack
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
```

## Usage

```bash
applytrack add "Siemens" "Werkstudent Software" --location Berlin --source LinkedIn --deadline 2026-12-01
applytrack list
applytrack list --status applied
applytrack move 1 applied
applytrack show 1
applytrack delete 1
```

The database lives at `~/.applytrack/applytrack.db`. Override it with the
`APPLYTRACK_DB` environment variable.

## Architecture

```
src/applytrack/
  models.py      Application dataclass, Status enum, allowed transitions
  repository.py  SQLite persistence (no business rules)
  cli.py         Typer commands, thin layer over models and repository
tests/           pytest suite
```

The domain rules (status transitions) live in `models.py` and know nothing
about storage or the CLI, so a web API can reuse them later.

## Development

```bash
pytest
ruff check .
```

CI runs both on every push and pull request.

## License

MIT
"# Applytrack" 
