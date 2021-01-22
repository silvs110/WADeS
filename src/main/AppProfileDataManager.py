import json
import logging
from pathlib import Path
from typing import List, Dict, Union

import paths
from src.main.AppProfile import AppProfile
from src.utils.error_messages import expected_type_but_received_message


class AppProfileDataManager:

    __default_app_profiles_file = paths.APP_PROF_DATA_PATH

    @staticmethod
    def save_app_profiles(app_profiles: List[AppProfile], app_profile_file: Union[str, Path] = __default_app_profiles_file) -> None:
        """
        Saves the appProfile in the file specified by app_profile_file.
        If no app_profile_file value is provided, it uses the default file, defined in `paths.py`
        :raises TypeError if app_profiles is not of type 'List[AppProfile]',
                or if app_profile_file is not of type 'str' or 'pathlib.Path'.
        :param app_profiles: the list of AppProfiles to save.
        :type app_profiles: List[AppProfile]
        :param app_profile_file: The name of the file to save the application profiles.
        :type app_profile_file: Union[str, pathlib.Path]
        """
        if not isinstance(app_profiles, list):
            raise TypeError(expected_type_but_received_message.format("app_profiles", "List[AppProfile]", app_profiles))

        if not isinstance(app_profile_file, (str, Path)):
            raise TypeError(
                expected_type_but_received_message.format(
                    "app_profile_file",
                    "Union[str, pathlib.Path]",
                    app_profile_file
                )
            )

        app_profiles_dict_list = dict()
        for app_profile in app_profiles:

            if not isinstance(app_profile, AppProfile):
                raise TypeError(
                    expected_type_but_received_message.format("app_profiles", "List[AppProfile]", app_profiles))

            app_profiles_dict_list[app_profile.get_application_name()] = app_profile.dict_format()
        try:
            app_profiles_json = json.dumps(app_profiles_dict_list)
            with open(app_profile_file, 'w') as file:
                file.write(app_profiles_json)
        except (IOError, OSError, json.JSONDecodeError) as error:
            logging.error(error)

    @staticmethod
    def get_saved_profiles(app_profile_file: Union[str, Path] = __default_app_profiles_file) -> List[AppProfile]:
        """
        Retrieves the saved profiles from the provided app_profile_file.
        If no app_profile_file value is specified, it uses the default file, defined in `paths.py`.
        :raises TypeError if app_profile_file is not of type 'str' or 'pathlib.Path'.
        :param app_profile_file: The name of the file to save the application profiles.
        :type app_profile_file: Union[str, pathlib.Path]
        :return: a list of AppProfiles.
        :rtype: List[AppProfile]
        """

        if not isinstance(app_profile_file, (str, Path)):
            raise TypeError(
                expected_type_but_received_message.format(
                    "app_profile_file",
                    "Union[str, pathlib.Path]",
                    app_profile_file
                )
            )

        app_profiles = list()

        app_profiles_dict = AppProfileDataManager.get_saved_profiles_as_dict(app_profile_file=app_profile_file)

        for app_name, app_profile_dict in app_profiles_dict.items():
            app_profile = AppProfile(application_name=app_name)
            app_profile.set_value_from_dict(app_profile_dict=app_profile_dict)
            app_profiles.append(app_profile)

        return app_profiles

    @staticmethod
    def get_saved_profiles_as_dict(app_profile_file: Union[str, Path] = __default_app_profiles_file) -> Dict[str, dict]:
        """
        Retrieves the saved profiles from the provided app_profile_file.
        If no app_profile_file value is specified, it uses the default file, defined in `paths.py`.
        :raises TypeError if app_profile_file is not of type 'str' or 'pathlib.Path'.
        :param app_profile_file: The name of the file to save the application profiles.
        :type app_profile_file: Union[str, pathlib.Path]
        :return: A dictionary of the application profile names to their respective AppProfile information.
        :rtype: Dict[str, dict]
        """

        if not isinstance(app_profile_file, (str, Path)):
            raise TypeError(
                expected_type_but_received_message.format(
                    "app_profile_file",
                    "Union[str, pathlib.Path]",
                    app_profile_file
                )
            )

        app_profiles = dict()
        try:
            with open(app_profile_file, 'r') as file:
                app_profiles_json = file.read()
                app_profiles = json.loads(app_profiles_json)

        except (IOError, OSError, json.JSONDecodeError) as error:
            logging.error(error)

        return app_profiles
