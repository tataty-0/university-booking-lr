from pathlib import Path

from alembic.config import Config

from alembic import command

ROOT = Path(__file__).resolve().parent.parent


def _config(db_path: str) -> Config:
    cfg = Config(str(ROOT / "alembic.ini"))
    cfg.set_main_option("script_location", str(ROOT / "alembic"))
    cfg.set_main_option("sqlalchemy.url", f"sqlite:///{db_path}")
    return cfg


def upgrade(db_path: str, revision: str = "head") -> None:
    command.upgrade(_config(db_path), revision)


def downgrade(db_path: str, revision: str) -> None:
    command.downgrade(_config(db_path), revision)


if __name__ == "__main__":
    import sys

    from app.config import Settings

    upgrade(Settings.from_env().db_path, sys.argv[1] if len(sys.argv) > 1 else "head")
