# -*- coding: utf-8 -*-
import logging
from pathlib import Path
from utils.db import InitDB
from utils.db.load_maps import insert_maps_from_wargaming_api
from utils.db.load_ships import insert_ships_from_wargaming_api
from utils.db.support import AssistFunction, AppProperties
from utils.parser_replays import parse_from_directory

if __name__ == '__main__':
    path = 'E:\\games\\World_of_Warships\\replays'
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(levelname)s %(message)s')
    db = InitDB('sqlite:///' + Path().cwd().joinpath('db/app.db').__str__())
    app_properties = AppProperties(db)
    assist_function = AssistFunction(db)

    app_properties.init_property()

    insert_ships_from_wargaming_api(db)
    insert_maps_from_wargaming_api(db)

    update_date = parse_from_directory(path, db, last_updated_date=app_properties.last_update_date)
    logging.info('дата и время запуска парсинга %s', update_date)
    app_properties.last_update_date = update_date

    assist_function.update_matchmaker_level()
    assist_function.update_number_of_platoon_member()
