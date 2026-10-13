# University Classroom Booking Service

Навчальний проєкт: сервіс бронювання університетських аудиторій (FastAPI, SQLite).

## Запуск

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt
uvicorn app.main:app --reload
```

Перевірка: `curl http://127.0.0.1:8000/health`

## Розробка

```bash
ruff check .
pytest -q
python scripts/build_release.py
```

## Посилання

- Jira: https://knu-team-f0xkp8mm.atlassian.net/jira/software/projects/BOOK
- Confluence: https://knu-team-f0xkp8mm.atlassian.net/wiki/spaces/BOOK
