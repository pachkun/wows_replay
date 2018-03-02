# -*- coding: utf-8 -*-
import logging
import struct
import json
import time
from io import BytesIO
from pathlib import Path
from BattleInfo import BattleInfo
from ParserException import ParserError, HeaderError, DBError
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


def parser_from_file(file_path: str):
    with open(file_path, 'rb') as file:
        try:
            battle_get_or_create(parse_replay(file))
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
def parse_from_directory(directory_path: str):
    for file_path in Path(directory_path).glob('**/*.wowsreplay'):
        parser_from_file(file_path)


if __name__ == '__main__':
    path = 'E:\\games\\World_of_Warships\\replays'
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(levelname)s %(message)s')
    insert_ships_from_wargaming_api()
    insert_maps_from_wargaming_api()
    parse_from_directory(path)
