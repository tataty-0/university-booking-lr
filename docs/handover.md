# Handover Guide

Інструкція запуску з чистого середовища (Python 3.12+, git).

## Кроки
1. `git clone https://github.com/tataty-0/university-booking-lr.git && cd university-booking-lr`
2. `git checkout v2.0`
3. `python -m venv .venv && source .venv/bin/activate && pip install -r requirements-dev.txt`
4. Конфігурація: `export BOOKING_DB_PATH=/шлях/до/booking.db` (каталог має існувати)
5. Міграції: `python -m app.migrations`
6. (Опційно) відновити навчальну копію БД: `python scripts/backup_db.py restore backup/teaching.db $BOOKING_DB_PATH`, потім `python -m app.migrations`
7. Запуск: `uvicorn app.main:app --host 0.0.0.0 --port 8000`
8. Перевірка: `python scripts/smoke_test.py http://127.0.0.1:8000`

## Основний сценарій
Відкрити `/`, вибрати користувача, перевірити доступність, створити бронювання, переглянути «Мої бронювання», скасувати.
Для аудиторії понад 100 місць статус PENDING; адміністратор (`admin`) підтверджує на `/admin.html`.

## Резервні копії
`python scripts/backup_db.py backup $BOOKING_DB_PATH backup/teaching.db`

## Діагностика
Див. `docs/operations.md`: `/health`, формат логів, перевірка шляху БД.

## Відомі обмеження
- Автентифікація навчальна (заголовок `X-User-Id`).
- SQLite: один писач одночасно.
- Відкат міграції v2.0 втратний (`docs/migration-v2.md`).
