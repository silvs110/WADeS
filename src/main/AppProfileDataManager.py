import json
import logging
from typing import List

import paths
from src.main.AppProfile import AppProfile
from src.utils.error_messages import expected_type_but_received_message


class AppProfileDataManager:

    @staticmethod
    def save_app_profiles(app_profiles: List[AppProfile]) -> None:
        """
        Saves the appProfile in the file specified in path.py.
        :raises TypeError if app_profiles is not of type 'List[AppProfile]'.
        :param app_profiles: the list of AppProfiles to save.
        :type app_profiles: List[AppProfile]
        """
        if not isinstance(app_profiles, list):
            raise TypeError(expected_type_but_received_message.format("app_profiles", "List[AppProfile]", app_profiles))

        app_profiles_dict_list = dict()
        for app_profile in app_profiles:

            if not isinstance(app_profile, AppProfile):
                raise TypeError(
                    expected_type_but_received_message.format("app_profiles", "List[AppProfile]", app_profiles))

            app_profiles_dict_list[app_profile.get_application_name()] = app_profile.dict_format()
        try:
            app_profiles_json = json.dumps(app_profiles_dict_list)
            with open(paths.APP_PROF_DATA_PATH, 'w') as file:
                file.write(app_profiles_json)
        except (IOError, OSError, json.JSONDecodeError) as error:
            logging.error(error)

    @staticmethod
    def get_saved_profiles() -> List[AppProfile]:
        """
        Retrieves the saved profiles from the specified file defined in 'paths.py'.
        :return: a list of AppProfiles.
        :rtype: List[AppProfile]
        """
        app_profiles = list()
        try:
            with open(paths.APP_PROF_DATA_PATH, 'r') as file:
                app_profiles_json = file.read()
                app_profiles_dict = json.loads(app_profiles_json)

                for app_name, app_profile_dict in app_profiles_dict.items():
                    app_profile = AppProfile(application_name=app_name)
                    app_profile.set_value_from_dict(app_profile_dict=app_profile_dict)
                    app_profiles.append(app_profile)

        except (IOError, OSError, json.JSONDecodeError) as error:
            logging.error(error)

        return app_profiles
