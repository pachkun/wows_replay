# -*- coding: utf-8 -*-
from datetime import datetime
from typing import List, Tuple, Callable, Optional
from sqlalchemy import func, asc
from sqlalchemy.orm import Session

from ..BattleInfo import BattleInfo
from . import InitDB
from .db_model import Battle, BattleMember, Ship, Properties

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


class AppProperties:
    LAST_UPDATE_DATE = 'last_updated_date_of_relpays'
    LAST_UPDATE_DATE_INIT_VALUE = datetime(year=1971, month=1, day=1)

    def __init__(self, engine: InitDB):
        self.engine = engine

    def init_property(self):
        with self.engine.session_scope() as session:  # type: Session
            if self.last_updated_date_of_relpays is None:
                last_update_date = Properties(name=self.LAST_UPDATE_DATE,
                                              value=str(self.LAST_UPDATE_DATE_INIT_VALUE.timestamp()),
                                              comment='POSIX timestamp')
                session.add(
                    last_update_date)

    @property
    def last_updated_date_of_relpays(self) -> Optional[datetime]:
        with self.engine.session_scope() as session:  # type: Session
            last_update_date = session.query(Properties).filter_by(
                name=self.LAST_UPDATE_DATE).first()  # type: Properties
            if last_update_date is None:
                return None
            return datetime.fromtimestamp(float(last_update_date.value))

    @last_updated_date_of_relpays.setter
    def last_updated_date_of_relpays(self, last_update_date: datetime):
        with self.engine.session_scope() as session:  # type: Session
            result = session.query(Properties).filter_by(name=self.LAST_UPDATE_DATE).first()  # type: Properties
            result.value = last_update_date.timestamp()

