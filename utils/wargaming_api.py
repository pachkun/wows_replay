# -*- coding: utf-8 -*-
import logging
import requests
import typing
from functools import lru_cache

__author__ = 'pachkun'

module_logger = logging.getLogger(__name__)


class ShipInfo(typing.NamedTuple):
    wargaming_ship_id: int
    name: str
    nation: str
    type: str
    tier: int
    is_special: bool
    is_premium: bool


class MapInfo(typing.NamedTuple):
    map_id: int
    name: str
    description: str
    icon: str


class APIError(Exception):
    pass


class Players(typing.NamedTuple):
    name: str
    source_json: dict

    class RankInfo(typing.NamedTuple):
        max_rank: int
        stars: int
        rank: int

        @classmethod
        def from_json(cls, players_rank_info: dict) -> 'RankInfo':
            if players_rank_info is None:
                module_logger.warning('No data')
                return None
            try:
                return cls(
                    max_rank=players_rank_info['max_rank'],
                    stars=players_rank_info['stars'],
                    rank=players_rank_info['rank']
                )
            except KeyError:
                module_logger.warning('Failed parse rank_solo %s', players_rank_info, exc_info=True)
                return None

    class RankSolo(typing.NamedTuple):
        max_frags_battle: int
        draws: int
        battles: int
        wins: int
        losses: int
        frags: int
        max_damage_dealt: int
        all_damage_dealt: int
        max_planes_killed: int
        survived_wins: int
        survived_battles: int
        planes_killed: int
        ramming_frags: int
        main_battery_hits: int
        main_battery_shots: int
        main_battery_frags: int
        second_battery_hits: int
        second_battery_shots: int
        second_battery_frags: int
        torpedoes_hits: int
        torpedoes_shots: int
        torpedoes_frags: int
        aircraft_frags: int
        source_json: dict

        @property
        def percent_wins(self) -> float:
            return round(self.wins * 100 / self.battles, ndigits=2)

        @property
        def percent_survived(self) -> float:
            return round(self.survived_battles * 100 / self.battles, ndigits=2)

        @property
        def percent_survived_wins(self) -> float:
            return round(self.survived_wins * 100 / self.wins, ndigits=2)

        @property
        def avg_frags(self) -> float:
            return round(self.frags / self.battles, ndigits=2)

        @property
        def avg_dmg(self) -> float:
            return round(self.all_damage_dealt / self.battles, ndigits=2)

        @property
        def avg_plane_kills(self) -> float:
            return round(self.planes_killed / self.battles, ndigits=2)

        @property
        def percent_main_battery_hits(self) -> float:
            return round(self.main_battery_hits * 100 / self.main_battery_shots, ndigits=2)

        @property
        def percent_torpedoes_hits(self) -> float:
            return round(self.torpedoes_hits * 100 / self.torpedoes_shots, ndigits=2)

        @property
        def other_frags(self) -> int:
            return self.frags - self.aircraft_frags - self.main_battery_frags \
                   - self.torpedoes_frags - self.second_battery_frags

        @classmethod
        def from_json(cls, players_rank_solo: dict) -> 'RankSolo':
            if players_rank_solo is None:
                module_logger.warning('No data')
                return None
            try:
                return cls(
                    max_frags_battle=players_rank_solo['max_frags_battle'],
                    draws=players_rank_solo['draws'],
                    battles=players_rank_solo['battles'],
                    wins=players_rank_solo['wins'],
                    losses=players_rank_solo['losses'],
                    frags=players_rank_solo['frags'],
                    max_damage_dealt=players_rank_solo['max_damage_dealt'],
                    all_damage_dealt=players_rank_solo['damage_dealt'],
                    max_planes_killed=players_rank_solo['max_planes_killed'],
                    survived_wins=players_rank_solo['survived_wins'],
                    survived_battles=players_rank_solo['survived_battles'],
                    planes_killed=players_rank_solo['planes_killed'],
                    ramming_frags=players_rank_solo['ramming']['frags'],
                    main_battery_hits=players_rank_solo['main_battery']['hits'],
                    main_battery_shots=players_rank_solo['main_battery']['shots'],
                    main_battery_frags=players_rank_solo['main_battery']['frags'],
                    second_battery_hits=players_rank_solo['second_battery']['hits'],
                    second_battery_shots=players_rank_solo['second_battery']['shots'],
                    second_battery_frags=players_rank_solo['second_battery']['frags'],
                    torpedoes_hits=players_rank_solo['torpedoes']['hits'],
                    torpedoes_shots=players_rank_solo['torpedoes']['shots'],
                    torpedoes_frags=players_rank_solo['torpedoes']['frags'],
                    aircraft_frags=players_rank_solo['aircraft']['frags'],
                    source_json=players_rank_solo
                )
            except KeyError:
                module_logger.warning('Failed parse rank_solo %s', players_rank_solo, exc_info=True)
                return None

    rank_info: RankInfo = None
    rank_solo: RankSolo = None

    @classmethod
    def from_json(cls, player_name, data_json) -> 'Players':
        rank_info = Players.RankInfo.from_json(data_json['rank_info'])
        rank_solo_json = Players.RankSolo.from_json(data_json['rank_solo'])
        return Players(name=player_name,
                       rank_info=rank_info,
                       rank_solo=rank_solo_json,
                       source_json=data_json)


class WOWS:
    API_URL = 'https://api.worldofwarships.ru'
    SHIPS_ENCYCLOPEDIA = '/wows/encyclopedia/ships/'
    PLAYER = '/wows/account/list/'
    PLAYER_STAT_IN_RANK_BATTLE = '/wows/seasons/accountinfo/'
    MAP_ENCYCLOPEDIA = '/wows/encyclopedia/battlearenas/'

    def __init__(self, application_id):
        self.application_id = application_id

    def _parse_ship(self, json_data: dict) -> ShipInfo:
        for ship_id, ship_info in json_data['data'].items():
            yield ShipInfo(wargaming_ship_id=ship_id,
                           name=ship_info['name'],
                           nation=ship_info['nation'],
                           type=ship_info['type'],
                           tier=ship_info['tier'],
                           is_special=ship_info['is_special'],
                           is_premium=ship_info['is_premium'])

    def _request_api(self, url: str, params: dict) -> dict:
        try:
            params['application_id'] = self.application_id
            module_logger.info('connect to url %s params %s', url, params)
            response = requests.get(url, params=params, allow_redirects=False)
        except ConnectionError:
            module_logger.warning('Failed connections to api %s', url, exc_info=True)
            raise APIError('connection error')
        # TODO http code check, json() может вернуть exception
        return response.json()

    def _request_rank_info(self, account_id: int, season_num: int) -> dict:
        params = dict(
            account_id=account_id,
            season_id=season_num
        )
        return self._request_api(self.API_URL + self.PLAYER_STAT_IN_RANK_BATTLE, params=params)

    def ships_list(self) -> typing.List[ShipInfo]:
        ships = []
        page_num = 1
        while True:
            response = self._request_ships_encyclopedia(page_num)
            ships += list(self._parse_ship(response))
            if response['meta']['page_total'] == page_num:
                break
            page_num += 1
        module_logger.info('end ships_list count ship %s', len(ships))
        return ships

    def _request_ships_encyclopedia(self, page_num: int) -> dict:
        params = dict(
            fields='is_premium,is_special,name,nation,tier,type',
            page_no=page_num
        )
        return self._request_api(self.API_URL + self.SHIPS_ENCYCLOPEDIA, params=params)

    def _request_maps_encyclopedia(self) -> dict:
        return self._request_api(self.API_URL + self.MAP_ENCYCLOPEDIA, {})

    def maps_list(self) -> typing.List[MapInfo]:
        response = self._request_maps_encyclopedia()
        return list(self._parse_map(response))

    @lru_cache(maxsize=200)
    def players(self, name: str) -> typing.Union[int, None]:
        params = dict(
            application_id=self.application_id,
            search=name
        )
        response = self._request_api(self.API_URL + self.PLAYER, params=params)
        for account in response['data']:
            if account['nickname'] == name:
                return account['account_id']
        module_logger.info('player %s not found', name)
        return None

    def player_stat_in_ranked_battle(self, name: str, season_num: int) -> typing.Union[Players, None]:
        account_id = self.players(name)
        if account_id is None:
            return None
        rank_info_json = self._request_rank_info(account_id=account_id, season_num=season_num)
        players_seasons_info = rank_info_json['data'][str(account_id)]['seasons'][str(season_num)]
        return Players.from_json(player_name=name, data_json=players_seasons_info)

    def _parse_map(self, json_data: dict) -> MapInfo:
        for map_data in json_data['data'].values():
            yield MapInfo(map_id=map_data['battle_arena_id'],
                          name=map_data['name'],
                          icon=map_data['icon'],
                          description=map_data['description'])
