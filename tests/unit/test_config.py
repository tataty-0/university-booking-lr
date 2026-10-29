import pytest

from app.config import ConfigError, Settings
from app.container import build_container


def test_valid_path_passes(tmp_path):
    Settings(db_path=str(tmp_path / "booking.db")).validate()


def test_missing_directory_is_reported(tmp_path):
    with pytest.raises(ConfigError, match="does not exist"):
        Settings(db_path=str(tmp_path / "missing" / "booking.db")).validate()


def test_directory_instead_of_file_is_reported(tmp_path):
    with pytest.raises(ConfigError, match="directory"):
        Settings(db_path=str(tmp_path)).validate()


def test_container_refuses_to_start_with_invalid_config(tmp_path):
    with pytest.raises(ConfigError):
        build_container(Settings(db_path=str(tmp_path / "missing" / "booking.db")))
