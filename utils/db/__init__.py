# coding=utf-8
from contextlib import contextmanager
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from db.db_model import metadata


class InitDB:

    def __init__(self, path: str):

        self.engine = create_engine(path, echo=False)
        self.Session = sessionmaker(bind=self.engine)
        metadata.create_all(self.engine)

    @contextmanager
    def session_scope(self) -> Session:
        session = self.Session()
        try:
            yield session
            session.commit()
        except:
            session.rollback()
            raise
        finally:
            session.close()

