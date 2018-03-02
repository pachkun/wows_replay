# coding=utf-8
from contextlib import contextmanager
import pathlib
import os
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
        # TODO разобраться на что влияет expire_on_commit, какой сайд эффект
        session = self.Session(expire_on_commit=False)
        try:
            yield session
            session.commit()
        except:
            session.rollback()
            raise
        finally:
            session.close()


engine = InitDB(os.environ.get('test_sqlite') or 'sqlite:///' + pathlib.Path().cwd().joinpath('db/app.db').__str__())
