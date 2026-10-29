import os
from dataclasses import dataclass
from pathlib import Path


class ConfigError(Exception):
    """Raised when the runtime configuration cannot work."""


@dataclass(frozen=True)
class Settings:
    db_path: str = "booking.db"

    @classmethod
    def from_env(cls) -> "Settings":
        return cls(db_path=os.environ.get("BOOKING_DB_PATH", cls.db_path))

    def validate(self) -> None:
        """Fail fast with an actionable message instead of failing on the first request."""
        path = Path(self.db_path)
        if path.is_dir():
            raise ConfigError(f"BOOKING_DB_PATH points to a directory: {path}")
        directory = path.resolve().parent
        if not directory.is_dir():
            raise ConfigError(f"database directory does not exist: {directory} (BOOKING_DB_PATH)")
        if not os.access(directory, os.W_OK):
            raise ConfigError(f"database directory is not writable: {directory}")
        if path.exists() and not os.access(path, os.R_OK | os.W_OK):
            raise ConfigError(f"database file is not readable and writable: {path}")
