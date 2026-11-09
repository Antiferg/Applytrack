# Roadmap

Planned work, roughly in priority order. Each item should become a GitHub issue.

## Next

- [ ] `stats` command: applications per status, response rate, average days to first reply
- [ ] Follow-ups: `FollowUp` model with due dates and an `overdue` command
- [ ] CSV and JSON export / import
- [ ] Deadline warnings in `list` (highlight deadlines within 7 days)

## Then

- [ ] REST API (FastAPI) reusing the same models and repository
- [ ] Dockerfile and docker-compose
- [ ] Switch persistence to SQLAlchemy, with migrations (Alembic)
- [ ] API authentication

## Maybe

- [ ] Reminder notifications (email or desktop)
- [ ] Simple web dashboard
