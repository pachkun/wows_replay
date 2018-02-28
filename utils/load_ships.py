# -*- coding: utf-8 -*-
import logging
from utils import WOWS, ShipInfo, session
from utils.db_model import Nation, Ship, Shiptype

__author__ = 'pachkun'
module_logger = logging.getLogger(__name__)


def add_ship(ship: ShipInfo, nation: Nation, ship_type: Shiptype):
    module_logger.info('add ship %s', ship)
    if session.query(Ship).filter_by(wargaming_ship_id=ship.wargaming_ship_id).first() is not None:
        module_logger.warning('Такой кораболь уже существует %s', ship)
        return
    session.add(Ship(
        wargaming_ship_id=ship.wargaming_ship_id,
        name=ship.name,
        tier=ship.tier,
        is_premium=ship.is_premium,
        is_special=ship.is_special,
        nation=nation,
        ship_type=ship_type
    ))


def nation_get_or_create(nation: str) -> Nation:
    nation_id = session.query(Nation).filter_by(name=nation).first()
    if nation_id is None:
        nation_id = Nation(name=nation)
        session.add(nation_id)
    return nation_id


def ship_type_get_or_create(ship_type: str) -> Shiptype:
    ship_type_id = session.query(Shiptype).filter_by(name=ship_type).first()
    if ship_type_id is None:
        ship_type_id = Shiptype(name=ship_type)
        session.add(ship_type_id)
    return ship_type_id


def insert_ships() -> None:
    wows_api = WOWS(application_id='demo')
    ship_list = wows_api.ships_list()
    for ship in ship_list:
        nation = nation_get_or_create(ship.nation)
        ship_type = ship_type_get_or_create(ship.type)
        add_ship(ship, nation, ship_type)
    session.commit()
