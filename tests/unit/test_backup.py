import sqlite3

from scripts.backup_db import copy_database


def test_backup_copies_rows(tmp_path):
    source = tmp_path / "a.db"
    connection = sqlite3.connect(source)
    connection.execute("CREATE TABLE t (id INTEGER)")
    connection.execute("INSERT INTO t VALUES (1), (2)")
    connection.commit()
    connection.close()

    target = tmp_path / "backup" / "b.db"
    copy_database(str(source), str(target))

    restored = sqlite3.connect(target)
    assert restored.execute("SELECT COUNT(*) FROM t").fetchone()[0] == 2
    restored.close()
