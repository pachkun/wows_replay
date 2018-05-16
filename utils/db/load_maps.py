# -*- coding: utf-8 -*-
import logging
from sqlalchemy.orm import Session
from .db_model import Map
from . import InitDB
from wows_api import WOWS
from wows_api.wargaming_api import MapInfo

__author__ = 'pachkun'


def add_map(map_data: MapInfo, session: Session) -> None:
    logging.info('add map %s', map_data)
    if session.query(Map).filter_by(map_id=map_data.map_id).first() is not None:
        logging.warning('Такая карта уже существует%s', map_data)
        return
    session.add(Map(
        map_id=map_data.map_id,
        name=map_data.name,
        description=map_data.description,
        icon=map_data.icon
    ))


def insert_maps_from_wargaming_api(engine: InitDB) -> None:
    wows_api = WOWS(application_id='demo')
    map_list = wows_api.maps_list()
    with engine.session_scope() as session:
        for map_data in map_list:
            add_map(map_data, session)
