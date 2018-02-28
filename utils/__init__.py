# coding=utf-8
import pathlib
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from utils.db_model import Player, Ship, Shiptype, Nation, Battle, metadata
from utils.wargaming_api import WOWS, ShipInfo

engine = create_engine('sqlite:///' + pathlib.Path().cwd().joinpath('db/app.db').__str__(), echo=False)
Session = sessionmaker(bind=engine)
session = Session()
metadata.create_all(engine)
