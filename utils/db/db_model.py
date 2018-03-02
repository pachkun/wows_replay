# -*- coding: utf-8 -*-

from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

__author__ = 'pachkun'
Base = declarative_base()
metadata = Base.metadata  # type: MetaData


class Player(Base):
    __tablename__ = 'Players'
    player_id = Column(Integer, primary_key=True)
    nickname = Column(String)
    account_id = Column(Integer, nullable=True)

    def __init__(self, nickname: str, account_id: int = None):
        self.nickname = nickname
        self.account_id = account_id

    def __str__(self):
        return f'{self.nickname}'


class Nation(Base):
    __tablename__ = 'Nations'
    nation_id = Column(Integer, primary_key=True)
    name = Column(String(64), index=True, unique=True)

    def __str__(self):
        return f'{self.name}'


class Shiptype(Base):
    __tablename__ = 'Shiptype'
    ship_type_id = Column(Integer, primary_key=True)
    name = Column(String(64), index=True, unique=True)

    def __str__(self):
        return f'{self.name}'


class Ship(Base):
    __tablename__ = 'Ships'
    ship_id = Column(Integer, primary_key=True)
    wargaming_ship_id = Column(Integer, index=True, unique=True)
    name = Column(String(64))
    tier = Column(Integer)
    is_premium = Column(Boolean)
    is_special = Column(Boolean)
    nation_id = Column(Integer, ForeignKey('Nations.nation_id'))
    ship_type_id = Column(Integer, ForeignKey('Shiptype.ship_type_id'))
    ship_type = relationship('Shiptype', backref='ships')
    nation = relationship('Nation', backref='ships')

    def __str__(self):
        return f'Ship:{self.name} - {self.tier}|{self.ship_type}|{self.nation}|' \
               f' special={self.is_special}, premium={self.is_premium}'


class Battle(Base):
    __tablename__ = 'Battle'
    battle_id = Column(Integer, primary_key=True)
    battle_uid = Column(String, unique=True)
    date = Column(DateTime)
    type = Column(String)
    mode = Column(String)
    map_id = Column(Integer, ForeignKey('maps.map_id'))
    version = Column(String)
    player_id = Column(Integer, ForeignKey('Players.player_id'))
    player_ship_id = Column(Integer, ForeignKey('Ships.ship_id'))
    player = relationship('Player', backref='protagonist')
    ship = relationship('Ship',  backref='protagonist_ship')

    def __str__(self):
        return f'{self.battle_uid}'


class BattleMember(Base):
    __tablename__ = 'BattleMembers'
    battle_member_id = Column(Integer, primary_key=True)
    player_id = Column(Integer, ForeignKey('Players.player_id'))
    ship_id = Column(Integer, ForeignKey('Ships.ship_id'))
    relation = Column(Integer)
    battle_id = Column(Integer, ForeignKey('Battle.battle_id'))
    player = relationship('Player', backref='battle_member')
    ship = relationship('Ship',  backref='battle_member_ship')
    battle = relationship('Battle',  backref='battles')

    def __str__(self):
        return f'{self.player_id} {self.relation}'


class Map(Base):
    __tablename__ = 'maps'
    map_id = Column(Integer, primary_key=True)
    name = Column(String)
    description = Column(String)
    icon = Column(String)
