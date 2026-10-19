# Quality Verification

Пороги задано в `docs/requirements.md` до вимірювання. Перевірки виконуються автоматично:

```bash
python scripts/measure_quality.py
```

| ID | Перевірка | Тест |
|---|---|---|
| QR-01 | чуже скасування завжди відхиляється (403), стан не змінюється | `test_qr01_foreign_cancellation_is_always_rejected` |
| QR-02 | усі бронювання зберігаються після перезапуску застосунку | `test_qr02_bookings_are_preserved_after_restart` |
| QR-03 | p95 створення бронювання ≤ 200 мс на 200 запитах | `test_qr03_booking_creation_p95_is_below_threshold` |

Фактичні результати кожного запуску публікуються на сторінці Quality Verification у Confluence.
