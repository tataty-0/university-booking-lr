"""SQLite backup and restore: python scripts/backup_db.py backup|restore <source> <target>"""

import sqlite3
import sys
from pathlib import Path


def copy_database(source: str, target: str) -> None:
    if not Path(source).is_file():
        raise SystemExit(f"source database not found: {source}")
    Path(target).parent.mkdir(parents=True, exist_ok=True)
    src = sqlite3.connect(source)
    dst = sqlite3.connect(target)
    try:
        src.backup(dst)
    finally:
        dst.close()
        src.close()


def main(argv: list[str]) -> int:
    if len(argv) != 4 or argv[1] not in {"backup", "restore"}:
        print(__doc__)
        return 2
    _, action, source, target = argv
    copy_database(source, target)
    print(f"{action} completed: {source} -> {target}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
