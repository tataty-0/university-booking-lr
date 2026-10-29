# Operations

## Конфігурація
| Змінна | Значення за замовчуванням | Опис |
|---|---|---|
| `BOOKING_DB_PATH` | `booking.db` | шлях до файлу SQLite |

Під час старту конфігурація перевіряється: каталог бази має існувати й бути доступним для запису.
Помилка конфігурації зупиняє запуск із зрозумілим повідомленням.

## Health
`GET /health` виконує реальний запит до БД.
- 200: `{"status": "ok", "database": "ok", "rooms": N, "bookings": M}`
- 503: `{"status": "degraded", "database": "unavailable"}` — БД недоступна або схема не застосована.

## Логи
Формат запиту: `request method=POST path=/api/bookings status=201 duration_ms=3.4 user=1`.
Старт: `starting version=... db_path=...`. Збої БД логуються на рівні ERROR з причиною.

## Діагностика
1. `curl /health` — стан БД і кількість записів.
2. Лог застосунку — шлях БД у рядку `starting` і ERROR-записи.
3. Порівняти `db_path` з очікуваним значенням `BOOKING_DB_PATH`.
