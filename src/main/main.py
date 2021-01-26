from pprint import pprint
from time import sleep

import psutil

from src.main.psHandler.AppProfileDataManager import AppProfileDataManager
from src.main.psHandler.ProcessHandler import ProcessHandler

process_handler = ProcessHandler()


def process_handler_run():
    process_handler.collect_running_processes_information()
    app_profiles = process_handler.get_registered_app_profiles_as_dict()
    pprint(app_profiles)
    return process_handler.get_registered_app_profiles_list()


def connect_to_db():
    app_db_manager = AppProfileDataManager()


def app_profile_json():
    app_profiles = process_handler_run()
    AppProfileDataManager.save_app_profiles(app_profiles=app_profiles)


for i in range(0, 10):
    app_profile_json()
ls = AppProfileDataManager.get_saved_profiles_as_dict()
pprint(ls)
