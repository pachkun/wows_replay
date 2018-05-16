# -*- coding: utf-8 -*-
import json
import unittest
from datetime import datetime

from utils.parser_replays import parse_replay
from utils.BattleInfo import BattleInfo
from utils.ParserException import HeaderError, ParserError
from tests import TEST_DATE_DIRECTORY

__author__ = 'pachkun'


class TestBattleInfoClass(unittest.TestCase):
    dict_vehicles = {"vehicles": [
        {
            "shipId": 4181637072,
            "relation": 1,
            "id": 427362,
            "name": "suroviy78"
        },
        {
            "shipId": 4076746192,
            "relation": 0,
            "id": 537207779,
            "name": "maikl_nepobedimyj"
        },
        {
            "shipId": 3552491216,
            "relation": 2,
            "id": 292470,
            "name": "charli51"
        },
        {
            "shipId": 4292818736,
            "relation": 2,
            "id": 579882,
            "name": "60026081"
        },
        {
            "shipId": 4282333168,
            "relation": 1,
            "id": 537201774,
            "name": "andron23Volyn"
        }]}

    def setUp(self):
        with open(TEST_DATE_DIRECTORY.joinpath('example/battle_info_rank.json'), 'r') as file:
            battle_info_json = json.loads(file.read())
        self.battle_info = BattleInfo(battle_info_json)

    def test_player_name(self):
        self.assertEqual(self.battle_info.player_name, "pachkunishka")

    def test_battle_date(self):
        self.assertEqual(self.battle_info.date,
                         datetime(day=10, month=1, year=2018, hour=22, minute=59, second=38))

    def test_version_game(self):
        self.assertEqual(self.battle_info.version_game, "0, 6, 15, 310510")

    def test_game_type(self):
        self.assertEqual(self.battle_info.type, "ranked")

    def test_map_id(self):
        self.assertEqual(self.battle_info.map_id, 9)

    def test_game_mode(self):
        self.assertEqual(self.battle_info.mode, 'Ranked_Domination')

    def test_player_ship_id(self):
        self.assertEqual(self.battle_info.player_ship_id, 3762272240)

    def test_vehicale_class_from_dict(self):
        data = {"shipId": 4181637072,
                "relation": 2,
                "id": 427362,
                "name": "suroviy78"}
        vehicle = self.battle_info.Vehicle.from_dict(data)
        self.assertEqual(vehicle.ship_id, 4181637072)
        self.assertEqual(vehicle.relation, 2)
        self.assertEqual(vehicle.player_name, 'suroviy78')

    def test_parse_vehicles(self):
        battle_info = BattleInfo(self.dict_vehicles)
        expecting_enemy_list = [
            BattleInfo.Vehicle(ship_id=3552491216, relation=2, player_name="charli51"),
            BattleInfo.Vehicle(ship_id=4292818736, relation=2, player_name="60026081")
        ]
        expecting_friend_list = [
            BattleInfo.Vehicle(ship_id=4181637072, relation=1, player_name="suroviy78"),
            BattleInfo.Vehicle(ship_id=4076746192, relation=0, player_name="maikl_nepobedimyj"),
            BattleInfo.Vehicle(ship_id=4282333168, relation=1, player_name="andron23Volyn")
        ]

        self.assertListEqual(list(battle_info.enemy_team_vehicles()), expecting_enemy_list)
        self.assertListEqual(list(battle_info.friend_team_vehicles()), expecting_friend_list)


class TestWowsParser(unittest.TestCase):
    # TODO доделать
    def test_integration(self):
        with open(TEST_DATE_DIRECTORY.joinpath('example/20180110_225938_PASA508-Enterprise_15_NE_north.wowsreplay'),
                  'rb') as file:
            battle_info = parse_replay(file)
            self.assertIsInstance(battle_info, BattleInfo)

    def test_header_error_for_not_replay_file(self):
        with open(TEST_DATE_DIRECTORY.joinpath('example/cef.txt'), 'rb') as file:
            with self.assertRaises(HeaderError):
                parse_replay(file)

    def test_parser_error_for_bad_json(self):
        with open(TEST_DATE_DIRECTORY.joinpath('example/error_json.wowsreplay'), 'rb') as file:
            with self.assertRaises(ParserError):
                parse_replay(file)

