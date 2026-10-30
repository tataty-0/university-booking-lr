# Міграція v1.0 → v2.0

Міграція `alembic/versions/0002_booking_states_and_roles.py`.

## Що змінюється
| Таблиця | Зміна |
|---|---|
| bookings | `status` (PENDING/ACTIVE/REJECTED/CANCELLED), `decided_by`, `decided_at`; `is_cancelled` видаляється |
| users | `role` (USER/ADMIN); додається користувач `admin` |

## Перетворення даних
- `is_cancelled = 0` → `ACTIVE`; `is_cancelled = 1` → `CANCELLED`.
- Ідентифікатори, власники та інтервали не змінюються.
- Існуючі бронювання великих аудиторій залишаються `ACTIVE` і не потребують підтвердження.

## Перевірка
`tests/migration/test_v1_to_v2.py` створює базу зі схемою v1.0, застосовує міграцію й перевіряє збереження записів.

## Відкат
Команда: `python -c "from app.migrations import downgrade; downgrade('booking.db', '0001')"`.
Відкат втратним: `PENDING` стає активним, `REJECTED` — скасованим, інформація про рішення адміністратора видаляється.
Перед міграцією на реальних даних потрібна резервна копія файлу БД.
