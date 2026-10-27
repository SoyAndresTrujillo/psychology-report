# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Stack

- Django 5.1, Python 3.11, PostgreSQL 15, `psycopg` 3, `python-dotenv`.
- No DRF, no JWT. API layer is plain `django.http.JsonResponse` views with `@csrf_exempt`.
- Dev runs in Docker via `docker-compose.dev.yml`. Host bind mount `.:/app` enables hot reload.

## Commands

All app-level commands run **inside the `psychologist_web` container** (the Python venv on host is not the source of truth).

```bash
# Start full stack (Postgres + web). Web container auto-runs `migrate` then `runserver`.
docker-compose -f docker-compose.dev.yml up -d

# Stop
docker-compose -f docker-compose.dev.yml down

# Migrations
docker exec -it psychologist_web python manage.py makemigrations
docker exec -it psychologist_web python manage.py migrate

# Single app migration
docker exec -it psychologist_web python manage.py makemigrations <app_name>

# Superuser
docker exec -it psychologist_web python manage.py createsuperuser

# Shell
docker exec -it psychologist_web python manage.py shell

# Tests — full suite, single app, single test
docker exec -it psychologist_web python manage.py test
docker exec -it psychologist_web python manage.py test appointments
docker exec -it psychologist_web python manage.py test appointments.tests.AppointmentTestCase.test_x

# Logs
docker logs -f psychologist_web
```

Web on `http://localhost:8000`, admin on `/admin`. Postgres exposed on host `5432`. Data persists in `./postgres_data/` (gitignored host dir, **do not** commit).

Env loaded from `.env` (copy from `.env.example`). Required keys: `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`, `SECRET_KEY`, `DEBUG`, `ALLOWED_HOSTS`. Inside Docker, `DB_HOST=postgres` (the service name), not `localhost`.

## Architecture

Django project = `psychologist_system/` (settings, root urls, wsgi/asgi). Six installed local apps, each a standard Django app (`models.py` + `forms.py` + `views.py` + `urls.py` + `admin.py` + `migrations/`):

- **accounts** — `Account` model. Single table for both patients and psychologists, discriminated by `role` field (`patient` | `psychologist`). All other apps reference `accounts.Account` via FK with `limit_choices_to={'role': ...}`. This is the project's core identity model — there is no usage of `django.contrib.auth.User` for domain users.
- **offices** — `DoctorsOffice`. Optional FK to a managing psychologist `Account`.
- **doctors** — `Doctor`. OneToOne to `Account` (psychologist role), FK to `DoctorsOffice`, `specialty` choice. Promotes a psychologist `Account` into a practicing doctor at a specific office.
- **appointments** — `Appointment`. FK patient `Account` + FK psychologist `Account` + `date` + `time` + `status`. `unique_together = ('psychologist', 'date', 'time')`. `clean()` blocks patient==psychologist.
- **polls** — `Polls` model (rating-style feedback). Added after the original four apps.
- **api** — JSON endpoints (see below). No `models.py` of its own.

URL composition (`psychologist_system/urls.py`): each app mounts its own `urls.py` under its prefix (`/accounts/`, `/offices/`, `/doctors/`, `/appointments/`, `/polls/`, `/api/`). The site root `/` is `accounts.views.home_view`.

Templates live in **project-level** `templates/` (registered via `TEMPLATES.DIRS`), not in per-app `templates/<app>/` dirs. `static/css/styles.css` is the single shared stylesheet; `STATICFILES_DIRS = [BASE_DIR / 'static']`, `STATIC_ROOT = BASE_DIR / 'staticfiles'`.

### Domain graph

```
Account(role=patient) ──┐
                        ├──< Appointment >── Account(role=psychologist)
                                                       │
                                                       ▼ (OneToOne)
                                                    Doctor ──FK──> DoctorsOffice
                                                                          ▲
                                                                          │ (FK psychologist, nullable)
                                                                   Account(role=psychologist)
```

A psychologist Account can manage offices (via `DoctorsOffice.psychologist`) **and** practice at one office (via `Doctor.doctors_office`). The two are independent — don't conflate them.

### API layer (`api/`)

All write endpoints are `POST`, `@csrf_exempt`, parse `json.loads(request.body)`. Response shape is uniform via `api_response(success, message, data, errors)`:

```json
{ "success": true, "message": "...", "data": {...}, "errors": {...} }
```

Endpoints (`api/urls.py`, prefix `/api/`):

| Method | Path | View |
|---|---|---|
| POST | `/api/accounts/create` | `create_account_api` — also auto-creates `Doctor` if role=psychologist and `doctors_office_id`+`specialty` provided |
| POST | `/api/offices/create` | `create_office_api` |
| POST | `/api/doctors/create` | `create_doctor_api` |
| POST | `/api/appointments/create` | `create_appointment_api` |
| POST | `/api/polls/create` | `create_poll_api` |
| GET  | `/api/appointment-report` | `appointment_report_api` — joins patient + psychologist + their office via `select_related` |

**Known gap**: `create_poll_api` in `api/views.py` references `Polls` but the symbol is **not imported** at module top. Any caller hitting `/api/polls/create` raises `NameError`. Import `from polls.models import Polls` before relying on it.

## Project conventions

- Each model carries a docstring citing "Single Responsibility Principle". Keep models thin and domain-only; do not move cross-cutting logic into them.
- Use `select_related` / `prefetch_related` for any view that crosses FKs (the appointment report is the existing pattern).
- Role-restricted FKs use `limit_choices_to={'role': '<patient|psychologist>'}` — preserve this on new relations to keep the admin sane.
- The web container runs `migrate` automatically on each `up`. **Don't** add startup logic that assumes a fresh DB.
- `.dockerignore` excludes `venv/`, `postgres_data/`, `__pycache__`. The host `venv/` is incidental; the container's interpreter is canonical.

## Windsurf rules note

`.windsurf/rules/*.md` (`django.md`, `python.md`, `docker.md`, `css.md`, `0planner.md`) describe an aspirational layout (DRF, JWT, `core/`, `config/settings/{base,dev,prod}.py`, API versioning). **The current code does not match.** It is plain Django views, single `settings.py`, no DRF, no API versioning. Treat the windsurf docs as future direction, not current truth — when in doubt, follow the code.
