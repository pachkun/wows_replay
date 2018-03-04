# -*- coding: utf-8 -*-
from typing import List, Tuple, Callable

from sqlalchemy import func, desc, asc

from BattleInfo import BattleInfo
from db import InitDB
from db.db_model import Battle, BattleMember, Ship

__author__ = 'pachkun'


class AssistFunction:

    def __init__(self, engine: InitDB):
        self.engine = engine

    def count_of_all_battles(self) -> int:
        with self.engine.session_scope() as session:
            return session.query(Battle).count()

    def group_by_number_player_battles(self, relation: List[int], sort: Callable = asc) -> List[Tuple[int]]:
        with self.engine.session_scope() as session:
            return session.query(BattleMember.player_id, func.count(BattleMember.player_id)).filter(
                BattleMember.relation.in_(relation)).group_by(
                BattleMember.player_id).order_by(sort(func.count(BattleMember.player_id))).all()

    # считаем членами отряда тех, кто сыграл в команде игрока больше 1% боев
    # (при маленьком количестов боев, фигово работает)
    def platoon_member(self) -> List[int]:
        all_battle = self.count_of_all_battles()
        platoon_member = filter(lambda x: x[1] > all_battle / 100,
                                self.group_by_number_player_battles(
                                    relation=[BattleInfo.FRIEND_TEAM, BattleInfo.PROTAGONIST]))
        return [x[0] for x in platoon_member]

    def list_platoon_battle(self) -> List[dict]:
        with self.engine.session_scope() as session:
            result = session.query(Battle.battle_id, func.count(Battle.battle_id), func.max(Ship.tier)) \
                .join(BattleMember, BattleMember.battle_id == Battle.battle_id) \
                .join(Ship, BattleMember.ship_id == Ship.ship_id) \
                .filter(BattleMember.relation.in_([BattleInfo.FRIEND_TEAM, BattleInfo.PROTAGONIST])) \
                .filter(BattleMember.player_id.in_(self.platoon_member())) \
                .filter(Battle.type == BattleInfo.RANDOM_BATTLE) \
                .group_by(Battle.battle_id)
        return [dict(battle_id=x[0], count=x[1], max_tier=x[2]) for x in result]

    def update_platoon_info(self) -> int:
        update_row = 0
        with self.engine.session_scope() as session:
            for battle in self.list_platoon_battle():
                update_row += session.query(Battle).filter(Battle.battle_id == battle['battle_id']) \
                    .update({'number_platoon_member': battle['count'], 'max_platoon_tier': battle['max_tier']})
        return update_row
