# -*- coding: utf-8 -*-
from typing import List, Tuple, Callable
from sqlalchemy import func, asc
from ..BattleInfo import BattleInfo
from . import InitDB
from .db_model import Battle, BattleMember, Ship

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

    def update_number_of_platoon_member(self):
        with self.engine.session_scope() as session:
            result = session.query(Battle, func.count(Battle.battle_id), func.max(Ship.tier)) \
                .join(BattleMember) \
                .join(Ship) \
                .filter(BattleMember.relation.in_([BattleInfo.FRIEND_TEAM, BattleInfo.PROTAGONIST])) \
                .filter(BattleMember.player_id.in_(self.platoon_member())) \
                .filter(Battle.type == BattleInfo.RANDOM_BATTLE) \
                .group_by(Battle.battle_id)
            for battle in result:
                battle[0].number_platoon_member = battle[1]
                battle[0].max_platoon_tier = battle[2]

    def update_matchmaker_level(self):
        with self.engine.session_scope() as session:
            result = session.query(Battle, func.max(Ship.tier)) \
                .join(BattleMember) \
                .join(Ship) \
                .group_by(Battle.battle_id)
            for battle in result:
                battle[0].matchmaking_level = battle[1]
