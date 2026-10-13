"""Build a release archive containing the application, VERSION and COMMIT files."""

import subprocess
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INCLUDE = ["app", "alembic", "alembic.ini", "static", "requirements.txt", "README.md", "docs"]


def git_commit() -> str:
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    except (OSError, subprocess.CalledProcessError):
        return "unknown"


def read_version() -> str:
    namespace: dict[str, str] = {}
    exec((ROOT / "app" / "version.py").read_text(), namespace)
    return namespace["__version__"]


def main() -> int:
    version = read_version()
    commit = git_commit()
    dist = ROOT / "dist"
    dist.mkdir(exist_ok=True)
    target = dist / f"university-booking-{version}.zip"
    with zipfile.ZipFile(target, "w", zipfile.ZIP_DEFLATED) as archive:
        for name in INCLUDE:
            path = ROOT / name
            if not path.exists():
                continue
            files = [path] if path.is_file() else [p for p in path.rglob("*") if p.is_file()]
            for file in files:
                if "__pycache__" in file.parts or file.suffix == ".pyc":
                    continue
                archive.write(file, file.relative_to(ROOT).as_posix())
        archive.writestr("VERSION", version + "\n")
        archive.writestr("COMMIT", commit + "\n")
    print(target)
    return 0


if __name__ == "__main__":
    sys.exit(main())
