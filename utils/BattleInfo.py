# -*- coding: utf-8 -*-
import hashlib
from typing import NamedTuple, List, Generator
from datetime import datetime

from ParserException import ParserError

__author__ = 'pachkun'


class BattleInfo:
    PROTAGONIST = 0
    FRIEND_TEAM = 1
    ENEMY_TEAM = 2

    class Vehicle(NamedTuple):
        ship_id: int
        relation: int
        player_name: str

        @classmethod
        def from_dict(cls, data: dict) -> 'Vehicle':
            return cls(ship_id=data['shipId'],
                       relation=data['relation'],
                       player_name=data['name'])

    def __init__(self, battle_info: dict):
        self.battle_info = battle_info
        self._friend_team_list = []  # type: List[Vehicle]
        self._enemy_team_list = []  # type: List[Vehicle]
        self._parse_vehicles()

    def _parse_vehicles(self):
        for vehicle_dict in self.battle_info['vehicles']:
            vehicle = self.Vehicle.from_dict(vehicle_dict)
            if vehicle.relation in (self.PROTAGONIST, self.FRIEND_TEAM):
                self._friend_team_list.append(vehicle)
            elif vehicle.relation == self.ENEMY_TEAM:
                self._enemy_team_list.append(vehicle)
            else:
                raise ParserError('неизветный тип отношений в команде :D', vehicle.relation)

    def __str__(self):
        return f'battle info {self.version_game} {self.map_id} {self.mode} {self.type} ' \
               f'{sum(v.ship_id for v in self.enemy_team_vehicles())}' \
               f'{sum(v.ship_id for v in self.friend_team_vehicles())}'

    # не такой уж и unique, но локально совпасть не должен
    @property
    def unique_battle_id(self):
        return hashlib.md5(self.__str__().encode()).hexdigest()

    @property
    def player_name(self) -> str:
        return self.battle_info['playerName']

    @property
    def date(self) -> datetime:
        return datetime.strptime(self.battle_info['dateTime'], '%d.%m.%Y %H:%M:%S')

    @property
    def version_game(self) -> str:
        return self.battle_info['clientVersionFromExe']

    # полный списко вроде тут
    # https://developers.wargaming.net/reference/all/wows/encyclopedia/battletypes/?application_id=demo&r_realm=ru&run=1
    @property
    def type(self) -> str:
        return self.battle_info['matchGroup']

    # https://developers.wargaming.net/reference/all/wows/encyclopedia/battlearenas/?application_id=demo&r_realm=ru
    @property
    def map_id(self) -> int:
        return self.battle_info['mapId']

    # где полный списко взять фиг знает, всякие доминирование превосходства и т.п.
    @property
    def mode(self) -> str:
        return self.battle_info['logic']

    @property
    def player_ship_id(self) -> int:
        for vehicle in self._friend_team_list:
            if vehicle.relation == self.PROTAGONIST:
                return vehicle.ship_id

    def enemy_team_vehicles(self) -> Generator[Vehicle, None, None]:
        for vehicle in self._enemy_team_list:
            yield vehicle

    def friend_team_vehicles(self) -> Generator[Vehicle, None, None]:
        for vehicle in self._friend_team_list:
            yield vehicle
