# -*- coding: utf-8 -*-
import json
import unittest
from unittest.mock import patch
from utils import WOWS, ShipInfo
from wargaming_api import MapInfo

__author__ = 'pachkun'


class WargamingAPIClient(unittest.TestCase):

    def setUp(self):
        self.wagaming_api = WOWS(application_id='for_test')
        self.maxDiff = None

    def test_parse_map(self):
        icon = "http://glossary-ru-static.gcdn.co/icons/wows/current/spaces/00_CO_ocean_minimap_combined.png"
        battle_arena_id = 1
        name = "Океан"
        description = "Безымянные воды где-то в Атлантике."

        map_info = {"status": "ok", "meta": {"count": 3},
                    "data": {
                        "1": {
                            "description": description,
                            "icon": icon,
                            "battle_arena_id": battle_arena_id,
                            "name": name
                        }}}

        (result,) = self.wagaming_api.parse_map(map_info)  # type: MapInfo
        self.assertEqual(result.map_id, battle_arena_id)
        self.assertEqual(result.icon, icon)
        self.assertEqual(result.name, name)
        self.assertEqual(result.description, description)

    @patch("wargaming_api.WOWS._request_api")
    def test_receive_maps(self, mock_response):
        with open('./example/wargaming_api/maps.json', 'r') as file:
            mock_response.return_value = json.load(file)

        result = self.wagaming_api.maps_list()
        self.assertEqual(len(result), 37)

    def test_parse_ship(self):
        ship_id = '3332323024'
        name = "[Yamato]"
        is_special = False
        is_premium = True
        nation = "japan"
        tier = 10
        ship_type = "Battleship"

        ship_info = {"status": "ok", "meta": {"count": 100, "page_total": 3, "total": 273, "limit": 100, "page": 1},
                     "data": {
                         ship_id: {
                             "name": name,
                             "is_special": is_special,
                             "nation": nation,
                             "is_premium": is_premium,
                             "tier": tier,
                             "type": ship_type
                         }}}

        (result,) = self.wagaming_api.parse_ship(ship_info)  # type: ShipInfo
        self.assertEqual(result.wargaming_ship_id, ship_id)
        self.assertEqual(result.name, name)
        self.assertEqual(result.is_special, is_special)
        self.assertEqual(result.is_premium, is_premium)
        self.assertEqual(result.nation, nation)
        self.assertEqual(result.tier, tier)
        self.assertEqual(result.type, ship_type)

    @patch("wargaming_api.WOWS._request_api")
    def test_receive_ships(self, mock_response):
        count_page = 4
        with open('./example/wargaming_api/ships.json', 'r') as file:
            json_dict = json.load(file)
            json_dict['meta']['page_total'] = count_page
            mock_response.return_value = json_dict

        result = self.wagaming_api.ships_list()
        self.assertEqual(mock_response.call_count, count_page)
        self.assertEqual(len(result), count_page * 100)
