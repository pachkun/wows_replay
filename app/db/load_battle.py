# -*- coding: utf-8 -*-
from functools import lru_cache
from ..BattleInfo import BattleInfo
from ..ParserException import DBError
from . import InitDB
from .db_model import BattleMember, Player, Battle, Ship

__author__ = 'pachkun'


def player_get_or_create(nickname: str, session) -> Player:
    player = session.query(Player).filter_by(nickname=nickname).first()
    if player is None:
        player = Player(nickname=nickname)
        session.add(player)
        return player
    return player


def insert_battle_member(battle_member: BattleInfo.Vehicle, battle: Battle, session):
    battle_member_id = BattleMember(
        player=player_get_or_create(nickname=battle_member.player_name, session=session),
        relation=battle_member.relation,
        ship=get_ship(battle_member.ship_id, session=session),
        battle=battle
    )
    session.add(battle_member_id)


@lru_cache(maxsize=512)
def get_ship(wargaming_ship_id: int, session) -> Ship:
    ship = session.query(Ship).filter_by(wargaming_ship_id=wargaming_ship_id).first()
    if ship is None:
        raise DBError('Нет такого коробля ', wargaming_ship_id)
    return ship


def battle_get_or_create(battle_info: BattleInfo, engine: InitDB):
    with engine.session_scope() as session:
        if session.query(Battle).filter_by(battle_uid=battle_info.unique_battle_id).first() is not None:
            raise DBError('Такая битва уже существует ', battle_info.__str__())
        battle = Battle(
            battle_uid=battle_info.unique_battle_id,
            date=battle_info.date,
            type=battle_info.type,
            mode=battle_info.mode,
            map_id=battle_info.map_id,
            version=battle_info.version_game,
            player=player_get_or_create(nickname=battle_info.player_name, session=session),
            ship=get_ship(battle_info.player_ship_id, session),
            max_platoon_tier=get_ship(battle_info.player_ship_id, session).tier
        )
        session.add(battle)
        for friend in battle_info.friend_team_vehicles():
            insert_battle_member(friend, battle, session)
        for enemy in battle_info.enemy_team_vehicles():
            insert_battle_member(enemy, battle, session)
