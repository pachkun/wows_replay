# -*- coding: utf-8 -*-
import unittest
from datetime import datetime

import pytest
from sqlalchemy import desc
from app.db import InitDB
from app.BattleInfo import BattleInfo
from app.db.db_model import Battle
from app.db.support import AssistFunction, AppProperties
from tests import TEST_DATE_DIRECTORY

__author__ = 'pachkun'


class TestAssistFunction(unittest.TestCase):

    def setUp(self):
        self.engine = InitDB('sqlite:///' + TEST_DATE_DIRECTORY.joinpath('example//test_db/app.db').__str__())
        self.assist_function = AssistFunction(self.engine)

        self.battle_pvp_count_in_test_db = 3267
        self.battle_count_in_test_db = 3327
        self.first_battle_id = 1

        self.pachkunishka_id = 1
        self.number_of_pachkun_battle = 3327
        self.stowerx_id = 12
        self.number_of_stowerx_battle = 2806
        self.firezombi_id = 265
        self.number_of_firezombi_battle = 1942
        self.fallencrusade_id = 482

    def test_count_of_all_battles(self):
        self.assertEqual(self.battle_count_in_test_db, self.assist_function.count_of_all_battles())

    def test_number_of_battle_by_player(self):
        expect_first_three = [(self.pachkunishka_id, self.number_of_pachkun_battle),
                              (self.stowerx_id, self.number_of_stowerx_battle),
                              (self.firezombi_id, self.number_of_firezombi_battle)]
        result = self.assist_function.group_by_number_player_battles([BattleInfo.PROTAGONIST, BattleInfo.FRIEND_TEAM],
                                                                     sort=desc)
        self.assertListEqual(expect_first_three, result[:3])

    def test_platoon_member(self):
        expect_platoon_member = [self.fallencrusade_id, self.firezombi_id, self.stowerx_id, self.pachkunishka_id]
        self.assertListEqual(self.assist_function.platoon_member(), expect_platoon_member)

    def test_update_number_of_platoon_member(self):
        with self.engine.session_scope() as session:
            session.query(Battle).filter(Battle.battle_id == self.first_battle_id) \
                .update({'number_platoon_member': 0, 'max_platoon_tier': 0})

        self.assist_function.update_number_of_platoon_member()

        with self.engine.session_scope() as session:
            result = session.query(Battle).filter(Battle.battle_id == 1).first()  # type: Battle
            session.expunge_all()
        self.assertEqual(5, result.max_platoon_tier)
        self.assertEqual(2, result.number_platoon_member)

    def test_update_matchmaker_level(self):
        with self.engine.session_scope() as session:
            session.query(Battle).filter(Battle.battle_id == self.first_battle_id) \
                .update({'matchmaking_level': 0})

        self.assist_function.update_matchmaker_level()

        with self.engine.session_scope() as session:
            result = session.query(Battle).filter(Battle.battle_id == 1).first()  # type: Battle
            session.expunge_all()
        self.assertEqual(7, result.matchmaking_level)


@pytest.fixture()
def app_propeties():
    engine = InitDB('sqlite:///')
    return AppProperties(engine)


def test_last_update_date(app_propeties: AppProperties):
    assert app_propeties.last_updated_date_of_relpays is None, 'таблица пуста'
    app_propeties.init_property()
    assert app_propeties.last_updated_date_of_relpays == app_propeties.LAST_UPDATE_DATE_INIT_VALUE, 'инициализация и чтения'
    test_date = datetime(year=2019, month=4, day=29, hour=23, minute=31, second=1)
    app_propeties.last_updated_date_of_relpays = test_date
    assert app_propeties.last_updated_date_of_relpays == test_date, 'запись и чтение'
