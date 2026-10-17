from sqlalchemy import Engine, create_engine, event
from sqlalchemy.orm import Session, sessionmaker


def make_engine(db_path: str) -> Engine:
    """SQLite engine with explicit write transactions.

    pysqlite starts transactions lazily, so a check-then-insert sequence is not
    atomic by default. Taking the write lock with BEGIN IMMEDIATE serializes
    writers and makes the conflict check and insert one atomic step (ADR-002).
    """
    engine = create_engine(
        f"sqlite:///{db_path}",
        connect_args={"check_same_thread": False, "timeout": 10, "isolation_level": None},
    )

    @event.listens_for(engine, "connect")
    def configure_connection(dbapi_connection, _):
        dbapi_connection.execute("PRAGMA foreign_keys=ON")
        dbapi_connection.execute("PRAGMA busy_timeout=10000")

    @event.listens_for(engine, "begin")
    def begin_immediate(connection):
        connection.exec_driver_sql("BEGIN IMMEDIATE")

    return engine


def make_session_factory(engine: Engine) -> sessionmaker[Session]:
    return sessionmaker(engine, expire_on_commit=False)
