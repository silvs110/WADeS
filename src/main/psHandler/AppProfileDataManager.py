import ast
from pathlib import Path
from typing import List, Dict, Union

import pandas

import paths
from src.main.common.AppProfile import AppProfile
from src.main.common.AppProfileAttribute import AppProfileAttribute
from src.utils.error_messages import expected_type_but_received_message, file_support_type_error_message
from wades_config import app_profile_retrieval_chunk_size


class AppProfileDataManager:
    __default_app_profiles_file = paths.APP_PROF_DATA_FILE_PATH
    __supported_file_extensions = [".csv"]
    __column_names = [attr.name for attr in AppProfileAttribute] # Order is important

    @staticmethod
    def get_saved_profiles(app_profile_file: Union[str, Path] = __default_app_profiles_file) -> List[AppProfile]:
        """
        Retrieves the saved profiles from the provided app_profile_file.
        If no app_profile_file value is specified, it uses the default file, defined in `paths.py`.
        :raises TypeError if app_profile_file is not of type 'str' or 'pathlib.Path'.
        :raises ValueError if the file extension of the path is not supported.
        :param app_profile_file: The name of the file to save the application profiles.
        :type app_profile_file: Union[str, pathlib.Path]
        :return: a list of AppProfiles.
        :rtype: List[AppProfile]
        """

        AppProfileDataManager.__validate_path(app_profile_file)
        app_profiles = list()

        app_profiles_dict = AppProfileDataManager.get_saved_profiles_as_dict(app_profile_file=app_profile_file)

        for app_name, app_profile_dict in app_profiles_dict.items():
            app_profile = AppProfile(application_name=app_name)
            app_profile.set_value_from_dict(app_profile_dict=app_profile_dict)
            app_profiles.append(app_profile)

        return app_profiles

    @staticmethod
    def save_app_profiles(app_profiles: List[AppProfile],
                          app_profile_file: Union[str, Path] = __default_app_profiles_file) -> None:
        """
        Saves the appProfile in the file specified by app_profile_file.
        If no app_profile_file value is provided, it uses the default file, defined in `paths.py`
        :raises TypeError if app_profiles is not of type 'List[AppProfile]',
                or if app_profile_file is not of type 'str' or 'pathlib.Path'.
        :raises ValueError if the file extension of the path is not supported.
        :param app_profiles: the list of AppProfiles to save.
        :type app_profiles: List[AppProfile]
        :param app_profile_file: The name of the file to save the application profiles.
        :type app_profile_file: Union[str, pathlib.Path]
        """
        if not isinstance(app_profiles, list):
            raise TypeError(expected_type_but_received_message.format("app_profiles", "List[AppProfile]", app_profiles))

        AppProfileDataManager.__validate_path(app_profile_file)

        app_profile_list = list()
        for app_profile in app_profiles:

            if not isinstance(app_profile, AppProfile):
                raise TypeError(
                    expected_type_but_received_message.format("app_profiles", "List[AppProfile]", app_profiles))

            app_profile_dict = app_profile.dict_format()

            app_profile_list.append(app_profile_dict)

        data_frame = pandas.DataFrame(app_profile_list, columns=AppProfileDataManager.__column_names)
        data_frame.to_csv(app_profile_file, index=False)

    @staticmethod
    def get_saved_profiles_as_dict(app_profile_file: Union[str, Path] = __default_app_profiles_file) \
            -> Dict[str, dict]:
        """
        Retrieves the saved profiles from the provided app_profile_file.
        If no app_profile_file value is specified, it uses the default file, defined in `paths.py`.
        :raises TypeError if app_profile_file is not of type 'str' or 'pathlib.Path'.
        :raises ValueError if the file extension of the path is not supported.
        :param app_profile_file: The name of the file to save the application profiles.
        :type app_profile_file: Union[str, pathlib.Path]
        :return: A dictionary of the application profile names to their respective AppProfile information.
        :rtype: Dict[str, dict]
        """

        AppProfileDataManager.__validate_path(app_profile_file)

        app_profiles = dict()

        for batch in pandas.read_csv(app_profile_file, chunksize=app_profile_retrieval_chunk_size):
            dataframe_values = batch.values.tolist()
            for app_profile_info_str_format in dataframe_values:
                app_profile_info = []

                for i in range(0, len(app_profile_info_str_format)):
                    attribute = app_profile_info_str_format[i]
                    if i > 1:
                        attribute = ast.literal_eval(attribute)

                    app_profile_info.append(attribute)
                app_profile_zip = zip(AppProfileDataManager.__column_names, app_profile_info)
                app_profile = dict(app_profile_zip)
                app_name = app_profile_info_str_format[0]
                app_profiles[app_name] = app_profile

        return app_profiles

    @staticmethod
    def __validate_path(app_profile_file: Union[str, Path]) -> None:
        """
        Validates that the application profile file has a supported file extension.
        :raises TypeError if app_profile_file is not of type 'str' or 'pathlib.Path'.
        :raises ValueError if the file extension of the path is not supported.
        :param app_profile_file: The name of the file to save the application profiles.
        :type app_profile_file: Union[str, pathlib.Path]
        """
        if not isinstance(app_profile_file, (str, Path)):
            raise TypeError(
                expected_type_but_received_message.format(
                    "app_profile_file",
                    "Union[str, pathlib.Path]",
                    app_profile_file
                )
            )

        if isinstance(app_profile_file, Path):
            app_profile_file = str(app_profile_file.absolute())

        if not any(app_profile_file.endswith(extension)
                   for extension in AppProfileDataManager.__supported_file_extensions):
            raise ValueError(
                file_support_type_error_message.format(
                    AppProfileDataManager.__supported_file_extensions,
                    app_profile_file
                )
            )
