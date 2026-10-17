# University Classroom Booking Service

Навчальний проєкт: сервіс бронювання університетських аудиторій (FastAPI, SQLite).

## Запуск

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt
python -m app.migrations          # створює booking.db або BOOKING_DB_PATH
uvicorn app.main:app --reload
```

Перевірка: `python scripts/smoke_test.py http://127.0.0.1:8000`. Інтерфейс: http://127.0.0.1:8000/

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
