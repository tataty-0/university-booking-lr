import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    db_path: str = "booking.db"

    @classmethod
    def from_env(cls) -> "Settings":
        return cls(db_path=os.environ.get("BOOKING_DB_PATH", cls.db_path))
