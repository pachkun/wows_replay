# -*- coding: utf-8 -*-
import unittest
from pathlib import Path

from sqlalchemy import desc

from db import InitDB
from BattleInfo import BattleInfo
from db.support import AssistFunction

__author__ = 'pachkun'


class TestAssistFunction(unittest.TestCase):

    def setUp(self):
        self.engine = InitDB('sqlite:///' + Path().cwd().joinpath('example//test_db/app.db').__str__())
        self.assist_function = AssistFunction(self.engine)

        self.battle_pvp_count_in_test_db = 3248
        self.battle_count_in_test_db = 3308

        self.pachkunishka_id = 1
        self.number_of_pachkun_battle = 3308
        self.stowerx_id = 12
        self.number_of_stowerx_battle = 2791
        self.firezombi_id = 265
        self.number_of_firezombi_battle = 1933
        self.fallencrusade_id = 482

    def test_count_of_all_battles(self):
        self.assertEqual(self.assist_function.count_of_all_battles(), self.battle_count_in_test_db)

    def test_number_of_battle_by_player(self):
        expect_first_three = [(self.pachkunishka_id, self.number_of_pachkun_battle),
                              (self.stowerx_id, self.number_of_stowerx_battle),
                              (self.firezombi_id, self.number_of_firezombi_battle)]
        result = self.assist_function.group_by_number_player_battles([BattleInfo.PROTAGONIST, BattleInfo.FRIEND_TEAM],
                                                                     sort=desc)
        self.assertListEqual(result[:3], expect_first_three)

    def test_platoon_member(self):
        expect_platoon_member = [self.fallencrusade_id, self.firezombi_id, self.stowerx_id, self.pachkunishka_id]
        self.assertListEqual(self.assist_function.platoon_member(), expect_platoon_member)

    def test_list_platoon_battles(self):
        expect_result = [
            # взвод из двух
            {'battle_id': 3290, 'count': 2, 'max_tier': 10},
            # взод из 3 игроков, два на 7 уровне 1 на 6 уровне
            {'battle_id': 3297, 'count': 3, 'max_tier': 7},
            # без взвода
            {'battle_id': 3210, 'count': 1, 'max_tier': 8}, ]

        result = self.assist_function.list_platoon_battle()

        self.assertEqual(len(result), self.battle_pvp_count_in_test_db)
        for expect in expect_result:
            self.assertTrue(expect in result)

    def test_update_platoon_info(self):
        # TODO дополнить тест
        self.assertEqual(self.assist_function.update_platoon_info(), self.battle_pvp_count_in_test_db)
