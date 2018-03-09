# -*- coding: utf-8 -*-
import logging
import struct
import json
import time
from io import BytesIO
from pathlib import Path
from BattleInfo import BattleInfo
from ParserException import ParserError, HeaderError, DBError
from db import InitDB
from db.support import AssistFunction
from utils import insert_maps_from_wargaming_api, battle_get_or_create, insert_ships_from_wargaming_api

__author__ = 'pachkun'

REPLAY_HEADER = b'\x1224\x11'


def how_long(f):
    def tmp(*args, **kwargs):
        t = time.time()
        res = f(*args, **kwargs)
        logging.info("time request: %f" % (time.time() - t))
        return res

    return tmp


def parse_replay(file: BytesIO):
    def battle_info_block(handle) -> dict:
        (json_block_size,) = struct.unpack("I", handle.read(4))
        try:
            return json.loads(file.read(json_block_size))
        except Exception:
            raise ParserError('ошибка парсинга json с информацией о бое')

    # Заголовок файла
    header = file.read(4)
    if header != REPLAY_HEADER:
        raise HeaderError(header)

    # видимо количестов блоков, теперь всегда = 1
    (block_count,) = struct.unpack("I", file.read(4))

    # информация о составе команд
    battle_info = battle_info_block(file)

    return BattleInfo(battle_info)


def parser_from_file(file_path: str, engine: InitDB):
    with open(file_path, 'rb') as file:
        try:
            battle_get_or_create(parse_replay(file), engine)
            logging.info('Файл %s обработан ', file.name)
        except HeaderError as err:
            logging.error('Файл не явлется рееплем world of warships %s , header file %s', file.name, err)
        except ParserError as err:
            logging.error('Файл не явлется рееплем world of warships %s , %s', file.name, err)
        except DBError as err:
            logging.error('Ошибка вставки в БД %s , %s', file.name, err)
        except Exception as err:
            logging.exception('Какая то ошибка world of warships %s , %s', file.name, err)


@how_long
def parse_from_directory(directory_path: str, engine: InitDB):
    for file_path in Path(directory_path).glob('**/*.wowsreplay'):
        parser_from_file(file_path, engine)


if __name__ == '__main__':
    path = 'E:\\games\\World_of_Warships\\replays'
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(levelname)s %(message)s')
    db = InitDB('sqlite:///' + Path().cwd().joinpath('db/app.db').__str__())
    assist_function = AssistFunction(db)

    insert_ships_from_wargaming_api(db)
    insert_maps_from_wargaming_api(db)
    assist_function.update_matchmaker_level()
    assist_function.update_number_of_platoon_member()
    parse_from_directory(path, db)
