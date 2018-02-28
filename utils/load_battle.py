# -*- coding: utf-8 -*-
import logging

from BattleInfo import BattleInfo
from ParserException import DBError
from utils import Player, session, Battle, Ship
from utils.db_model import BattleMember

__author__ = 'pachkun'


def player_get_or_create(nickname: str) -> Player:
    player = session.query(Player).filter_by(nickname=nickname).first()
    if player is None:
        player = Player(nickname=nickname)
        session.add(player)
        session.commit()
    return player


def insert_battle_member(battle_member: BattleInfo.Vehicle, battle_id: int):
    battle_member_id = BattleMember(
        player_id=player_get_or_create(nickname=battle_member.player_name).player_id,
        relation=BattleInfo.FRIEND_TEAM if battle_member.relation == BattleInfo.PROTAGONIST else battle_member.relation,
        ship_id=get_ship_id(battle_member.ship_id).ship_id,
        battle_id=battle_id
    )
    session.add(battle_member_id)


def get_ship_id(wargaming_ship_id: int) -> Ship:
    ship = session.query(Ship).filter_by(wargaming_ship_id=wargaming_ship_id).first()
    if ship is None:
        session.rollback()
        raise DBError('Нет такого коробля ', wargaming_ship_id)
    return ship


def battle_get_or_create(battle_info: BattleInfo):
    if session.query(Battle).filter_by(battle_uid=battle_info.unique_battle_id).first() is not None:
        session.rollback()
        raise DBError('Такая битва уже существует ', battle_info)
    battle = Battle(
        battle_uid=battle_info.unique_battle_id,
        date=battle_info.date,
        type=battle_info.type,
        mode=battle_info.mode,
        map_id=battle_info.map_id,
        version=battle_info.version_game,
        player_id=player_get_or_create(nickname=battle_info.player_name).player_id,
        player_ship_id=get_ship_id(battle_info.player_ship_id).ship_id
    )
    session.add(battle)
    session.commit()
    for friend in battle_info.friend_team_vehicles():
        insert_battle_member(friend, battle.battle_id)
    for enemy in battle_info.enemy_team_vehicles():
        insert_battle_member(enemy, battle.battle_id)
    session.commit()
