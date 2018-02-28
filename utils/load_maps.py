# -*- coding: utf-8 -*-
import logging

from db_model import Map
from utils import session
from wargaming_api import MapInfo, WOWS

__author__ = 'pachkun'


def add_map(map_data: MapInfo):
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


def insert_maps() -> None:
    wows_api = WOWS(application_id='demo')
    map_list = wows_api.maps_list()
    for map_data in map_list:
        add_map(map_data)
    session.commit()
