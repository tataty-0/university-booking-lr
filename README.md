# University Classroom Booking Service

Навчальний проєкт: сервіс бронювання університетських аудиторій (FastAPI, SQLite).

## Запуск

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt
python -m app.migrations          # створює booking.db або BOOKING_DB_PATH
uvicorn app.main:app --reload
```

Перевірка: `python scripts/smoke_test.py http://127.0.0.1:8000`; поле `version` у `/health` має збігатися з номером релізу. Інтерфейс: http://127.0.0.1:8000/

Тестові користувачі: `alice` (1), `bob` (2), `carol` (3), передаються заголовком `X-User-Id`.

## Розробка

```bash
ruff check .
pytest -q
python scripts/build_release.py
```

## Посилання

- Jira: https://knu-team-f0xkp8mm.atlassian.net/jira/software/projects/BOOK
- Confluence: https://knu-team-f0xkp8mm.atlassian.net/wiki/spaces/BOOK

## Адміністратор (v2.0)

Бронювання аудиторій понад 100 місць мають статус `PENDING`. Адміністратор (користувач `admin`, id 4)
підтверджує або відхиляє запити на сторінці `/admin.html` або через `/api/admin/bookings/*`.
Інструкція передавання: `docs/handover.md`.

## Конкурентність

Створення бронювання виконується в транзакції `BEGIN IMMEDIATE`, тому паралельні запити
на один слот не можуть створити два активні бронювання (див. `docs/adr/ADR-002-concurrency.md`).
