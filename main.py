# -*- coding: utf-8 -*-
import logging
from pathlib import Path
from utils.db import InitDB
from utils.db.load_maps import insert_maps_from_wargaming_api
from utils.db.load_ships import insert_ships_from_wargaming_api
from utils.db.support import AssistFunction
from utils.parser_replays import parse_from_directory

if __name__ == '__main__':
    path = 'E:\\games\\World_of_Warships\\replays'
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(levelname)s %(message)s')
    db = InitDB('sqlite:///' + Path().cwd().joinpath('db/app.db').__str__())
    assist_function = AssistFunction(db)

    insert_ships_from_wargaming_api(db)
    insert_maps_from_wargaming_api(db)

    parse_from_directory(path, db)

    assist_function.update_matchmaker_level()
    assist_function.update_number_of_platoon_member()
