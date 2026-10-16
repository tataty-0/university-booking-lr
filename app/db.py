from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session, sessionmaker


def make_engine(db_path: str) -> Engine:
    return create_engine(
        f"sqlite:///{db_path}", connect_args={"check_same_thread": False, "timeout": 10}
    )


def make_session_factory(engine: Engine) -> sessionmaker[Session]:
    return sessionmaker(engine, expire_on_commit=False)
