# Архітектура

Модульний моноліт: API → сервіси застосунку → доменна логіка → репозиторії → SQLite.

## Контекст
```mermaid
flowchart LR
    U[Користувач] -->|HTTP| W[Браузерний UI]
    W -->|REST JSON| S[Сервіс бронювання]
    A[Адміністратор v2.0] -->|HTTP| W
    S --> D[(SQLite)]
```

## Компоненти
```mermaid
flowchart TB
    UI[static: HTML/CSS/JS] --> API[app.api: FastAPI-роутери]
    API --> SVC[app.services: RoomService, BookingService]
    SVC --> DOM[app.domain: інтервали, політики, стани]
    SVC --> REPO[app.repositories]
    REPO --> DB[(SQLite через SQLAlchemy)]
```

## Створення бронювання
```mermaid
sequenceDiagram
    participant UI
    participant API
    participant Service
    participant Repo
    participant DB
    UI->>API: POST /api/bookings
    API->>Service: create(user, room, start, end)
    Service->>Service: validate_interval
    Service->>DB: BEGIN IMMEDIATE
    Service->>Repo: find_conflicts(room, interval)
    Repo-->>Service: []
    Service->>Repo: add(booking)
    Service->>DB: COMMIT
    API-->>UI: 201 Created
```

## Основні контракти API (v1.0)
| Метод | Шлях | Опис | Помилки |
|---|---|---|---|
| GET | /health | стан сервісу | — |
| GET | /api/rooms | список аудиторій | — |
| GET | /api/rooms/{id}/availability?start&end | перевірка доступності | 422, 404 |
| POST | /api/bookings | створити бронювання | 422, 409, 404 |
| GET | /api/bookings/my | бронювання поточного користувача | 401 |
| POST | /api/bookings/{id}/cancel | скасувати своє бронювання | 403, 404, 409 |

Користувач ідентифікується заголовком `X-User-Id` (навчальні акаунти).
