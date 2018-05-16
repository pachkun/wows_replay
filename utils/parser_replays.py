# -*- coding: utf-8 -*-
import logging
import struct
import json
import time
from datetime import datetime
from pathlib import Path
from typing import BinaryIO
from .db.load_battle import battle_get_or_create
from .BattleInfo import BattleInfo
from .ParserException import ParserError, HeaderError, DBError
from .db import InitDB


__author__ = 'pachkun'

REPLAY_HEADER = b'\x1224\x11'


def how_long(f):
    def tmp(*args, **kwargs):
        t = time.time()
        res = f(*args, **kwargs)
        logging.info("time request: %f" % (time.time() - t))
        return res

    return tmp


def parse_replay(file: BinaryIO):
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
    if block_count > 1:
        raise ParserError('формат файла реплея изменен')

    # информация о составе команд
    battle_info = battle_info_block(file)

    return BattleInfo(battle_info)


def parser_from_file(file_path: Path, engine: InitDB):
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
def parse_from_directory(directory_path: str, engine: InitDB, last_updated_date: datetime = None) -> datetime:
    """
    Парсинг реплеев из каталога
    :param directory_path: путь к папке с файлами реплеев
    :param engine: движок БД
    :param last_updated_date: дата и время последнего загруженного реплея от которой парсить
            (если не заполнена перебирает все файлы)
    :return: Дата и время загрузки реплеев
    """
    start_parsing_date = datetime.now()
    for file_path in Path(directory_path).glob('**/*.wowsreplay'):
        if file_path.is_file():
            creation_file_date = datetime.fromtimestamp(file_path.stat().st_ctime)
            if last_updated_date is None or creation_file_date >= last_updated_date:
                parser_from_file(file_path, engine)
    return start_parsing_date
