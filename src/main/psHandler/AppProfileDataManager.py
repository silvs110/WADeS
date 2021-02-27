import ast
import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Union, Any, Set

import pandas
from pandas import DataFrame

import paths
import wades_config
from src.main.common.AppProfile import AppProfile
from src.main.common.AppSummary import AppSummary
from src.main.common.enum.AppProfileAttribute import AppProfileAttribute
from src.main.common.enum.AppSummaryAttribute import AppSummaryAttribute
from src.utils.error_messages import expected_type_but_received_message
from wades_config import app_profile_retrieval_chunk_size, datetime_format


class AppProfileDataManager:
    __path_to_use = paths.TEST_APP_PROF_DATA_DIR_PATH if wades_config.is_test else paths.APP_PROF_DATA_DIR_PATH
    __supported_file_extensions = [".csv"]
    __column_names = [attr.name for attr in AppProfileAttribute]  # Order is important
    __default_retrieval_timestamp_file = __path_to_use / wades_config.retrieval_timestamp_file_name
    __default_abnormal_apps_file = __path_to_use / wades_config.abnormal_apps_file_name

    @staticmethod
    def get_saved_profile(app_profile_name: str, base_path: Path = __path_to_use) -> Union[AppProfile, None]:
        """
        Retrieves the saved profiles from the provided app_profile_file.
        If no app_profile_file value is specified, it uses the default file, defined in `paths.py`.
        :raises TypeError if app_profile_file is not of type 'str' or 'pathlib.Path'.
        :param app_profile_name: The name of the application profile to retrieve.
        :type app_profile_name: str
        :param base_path: The base path to get the application profile from.
        :type base_path: pathlib.Path
        :return: a list of AppProfiles.
        :rtype: Union[AppProfile, None]
        """

        app_profile_dict = AppProfileDataManager.get_saved_profile_as_dict(app_profile_name, base_path)
        if app_profile_dict is None:
            return None
        app_profile = AppProfile(application_name=app_profile_name)
        app_profile.set_value_from_dict(app_profile_dict=app_profile_dict)

        return app_profile

    @staticmethod
    def save_app_profiles(app_profiles: List[AppProfile], retrieval_timestamp: datetime,
                          app_profile_base_dir: Path = __path_to_use,
                          retrieval_timestamp_file_path: Path = __default_retrieval_timestamp_file) -> None:
        """
        Saves the appProfiles in the file specified by app_profile_file.
        If no app_profile_file value is provided, it uses the default file, defined in `paths.py`
        :raises TypeError if app_profiles is not of type 'List[AppProfile]',
                or if app_profile_base_dir or retrieval_timestamp_file_path are not of type 'pathlib.Path',
                or if retrieval_timestamp is not of type 'datetime'.
        :param app_profiles: The list of AppProfiles to save.
        :type app_profiles: List[AppProfile]
        :param retrieval_timestamp: The latest retrieval timestamp of the AppProfile objects.
        :type retrieval_timestamp: datetime
        :param app_profile_base_dir: The base directory of app profiles files.
        :type app_profile_base_dir: pathlib.Path
        :param retrieval_timestamp_file_path: The path of the file to save the retrieval timestamp.
        :type retrieval_timestamp_file_path: Union[str, pathlib.Path]
        """
        if not isinstance(app_profiles, list):
            raise TypeError(expected_type_but_received_message.format("app_profiles", "List[AppProfile]", app_profiles))

        if not isinstance(app_profile_base_dir, Path):
            raise TypeError(expected_type_but_received_message.format("app_profile_base_dir",
                                                                      "pathlib.Path",
                                                                      app_profile_base_dir))

        if not isinstance(retrieval_timestamp, datetime):
            raise TypeError(expected_type_but_received_message.format("retrieval_timestamp", "datetime",
                                                                      retrieval_timestamp))

        if not isinstance(retrieval_timestamp_file_path, Path):
            raise TypeError(expected_type_but_received_message.format("retrieval_timestamp_file_path",
                                                                      "pathlib.Path",
                                                                      retrieval_timestamp_file_path))

        for app_profile in app_profiles:
            AppProfileDataManager.save_app_profile(app_profile, app_profile_base_dir)
            if not isinstance(app_profile, AppProfile):
                raise TypeError(
                    expected_type_but_received_message.format("app_profiles", "List[AppProfile]", app_profiles))

        AppProfileDataManager.save_last_retrieved_data_timestamp(retrieval_timestamp, retrieval_timestamp_file_path)

    @staticmethod
    def save_app_profile(app_profile: AppProfile, base_path: Path = __path_to_use) -> None:
        """
        Save an application profile in the specified base directory.
        :raises TypeError if app_profile is not of type 'AppProfile',
            or if base_path is not of type 'pathlib.Path'.
        :param app_profile: The application profile to save.
        :type app_profile: AppProfile
        :param base_path: The base path to save the application profile.
            It defaults to values paths.APP_PROF_DATA_DIR_PATH if is not running as a test and to
            paths.TEST_APP_PROF_DATA_DIR_PATH if it is.
        :type base_path: pathlib.Path
        """
        if not isinstance(app_profile, AppProfile):
            raise TypeError(expected_type_but_received_message.format("app_profile", "AppProfile", app_profile))

        if not isinstance(base_path, Path):
            raise TypeError(expected_type_but_received_message.format("base_path", "pathlib.Path", base_path))

        app_profile_file_path = AppProfileDataManager.__get_app_profile_file_path(
            app_profile_name=app_profile.get_application_name(), base_path=base_path)

        app_profile_dict = app_profile.dict_format()
        data_frame = pandas.DataFrame([app_profile_dict], columns=AppProfileDataManager.__column_names)
        data_frame.to_csv(app_profile_file_path, index=False)

    @staticmethod
    def __get_app_profile_file_path(app_profile_name: str, base_path: Path = __path_to_use) -> Path:
        """
        Gets the App Profile file path.
        :param app_profile_name: The name of the app profile.
        :type app_profile_name: str
        :param base_path: The base path to save the application profile.
            It defaults to values paths.APP_PROF_DATA_DIR_PATH if is not running as a test and to
            paths.TEST_APP_PROF_DATA_DIR_PATH if it is.
        :type base_path: pathlib.Path
        :return: The file path of the App profile.
        :rtype: pathlib.Path
        """
        if not isinstance(base_path, Path):
            raise TypeError(expected_type_but_received_message.format("base_path", "pathlib.Path", base_path))

        mapping_path = base_path / wades_config.app_profile_file_names_map
        data_frame = AppProfileDataManager.__get_saved_app_profiles_file_names_mapping_dataframe(base_path)
        matching_index = data_frame.index[data_frame[AppProfileAttribute.app_name.name] == app_profile_name].tolist()
        if len(matching_index) == 0:
            data_frame = data_frame.append({AppProfileAttribute.app_name.name: app_profile_name}, ignore_index=True)
            data_frame.to_csv(mapping_path)
        matching_index = data_frame.index[data_frame[AppProfileAttribute.app_name.name] == app_profile_name].tolist()
        index = matching_index[0]
        file_name = f"{index}.csv"
        return base_path / file_name

    @staticmethod
    def __get_saved_app_profiles_file_names_mapping_dataframe(base_path: Path = __path_to_use) -> DataFrame:
        """
        Get the dataframe containing the list of saved application names and their respective file names.
        :param base_path: The base path where to retrieve the application profile names.
            It defaults to values paths.APP_PROF_DATA_DIR_PATH if is not running as a test and to
            paths.TEST_APP_PROF_DATA_DIR_PATH if it is.
        :type base_path: pathlib.Path
        :return: The dataframe containing the list of saved application names and their respective file names.
        :rtype: pandas.DataFrame
        """

        if not isinstance(base_path, Path):
            raise TypeError(expected_type_but_received_message.format("base_path", "pathlib.Path", base_path))

        mapping_path = base_path / wades_config.app_profile_file_names_map
        if not mapping_path.exists():
            data_frame = pandas.DataFrame(columns=[AppProfileAttribute.app_name.name])
            data_frame.to_csv(mapping_path, index=True)
        return pandas.read_csv(mapping_path, index_col=0)

    @staticmethod
    def get_saved_app_profiles_names(base_path: Path = __path_to_use) -> Set[str]:
        """
        Gets the names of the saved application profiles.
        :param base_path: The base path where to retrieve the application profile names.
            It defaults to values paths.APP_PROF_DATA_DIR_PATH if is not running as a test and to
            paths.TEST_APP_PROF_DATA_DIR_PATH if it is.
        :type base_path: pathlib.Path
        :return: The names of the saved application profiles.
        :rtype: Set[str]
        """
        dataframe = AppProfileDataManager.__get_saved_app_profiles_file_names_mapping_dataframe(base_path)
        return set(dataframe[AppProfileAttribute.app_name.name].to_list())

    @staticmethod
    def get_saved_profile_as_dict(app_profile_name: str, base_path: Path = __path_to_use) \
            -> Union[Dict[str, Any], None]:
        """
        Retrieves the saved profiles from the provided app_profile_file.
        If no app_profile_file value is specified, it uses the default file, defined in `paths.py`.
        :raises TypeError if app_profile_name is not of type 'str',
            or if base_path is not of type 'pathlib.Path'.
        :param app_profile_name: The name of the application profile to retrieve.
        :type app_profile_name: str
        :param base_path: The base directory to find the application profile.
        :type base_path: Path
        :return: A dictionary of the application profile names to their respective AppProfile information.
        :rtype: Union[Dict[str, Any], None]
        """

        if not isinstance(app_profile_name, str):
            raise TypeError(expected_type_but_received_message.format("app_profile_name", str, app_profile_name))

        app_profile_file_path = AppProfileDataManager.__get_app_profile_file_path(app_profile_name,
                                                                                  base_path)
        try:
            values_raw = pandas.read_csv(app_profile_file_path)
            dataframe_values = values_raw.values.tolist()
            for app_profile_info_str_format in dataframe_values:
                app_profile_info = []

                for i in range(0, len(app_profile_info_str_format)):
                    attribute = app_profile_info_str_format[i]
                    if i > 1:
                        attribute = ast.literal_eval(attribute)

                    app_profile_info.append(attribute)
                app_profile_zip = zip(AppProfileDataManager.__column_names, app_profile_info)
                return dict(app_profile_zip)
        except FileNotFoundError:
            return

    @staticmethod
    def save_last_retrieved_data_timestamp(retrieval_timestamp: datetime,
                                           retrieval_timestamp_file_path: Path = __default_retrieval_timestamp_file) \
            -> None:
        """
        Save the last retrieved timestamp in the specified directory.
        :raises TypeError if retrieval_timestamp is not of type 'datetime',
            or if retrieval_timestamp_file_path is not of type 'pathlib.Path'.
        :param retrieval_timestamp: The retrieved timestamp to save.
        :type retrieval_timestamp: datetime
        :param retrieval_timestamp_file_path: The path of the file where the retrieval timestamp is saved.
        :type retrieval_timestamp_file_path: pathlib.Path
        """

        if not isinstance(retrieval_timestamp_file_path, Path):
            raise TypeError(expected_type_but_received_message.format("retrieval_timestamp_file_path",
                                                                      "pathlib.Path",
                                                                      retrieval_timestamp_file_path))

        if not isinstance(retrieval_timestamp, datetime):
            raise TypeError(expected_type_but_received_message.format("retrieval_timestamp", "datetime",
                                                                      retrieval_timestamp))

        with open(AppProfileDataManager.__default_retrieval_timestamp_file, "w") as file:
            file.write(retrieval_timestamp.strftime(datetime_format))

    @staticmethod
    def get_last_retrieved_data_timestamp(retrieval_timestamp_file_path: Union[str, Path]
                                          = __default_retrieval_timestamp_file) -> Union[datetime, None]:
        """
        Get the latest retrieved data timestamp from the specified file.
        :param retrieval_timestamp_file_path: The latest retrieved data timestamp file path.
        :type retrieval_timestamp_file_path: Union[str, Path]
        :return: The latest retrieved timestamp, which is saved on the specified file.
        :rtype: Unions[datetime, None]
        """
        try:
            with open(retrieval_timestamp_file_path, "r") as file:
                data = file.read()
                return datetime.strptime(data, datetime_format)

        except (FileNotFoundError, ValueError):
            return None

    @staticmethod
    def save_abnormal_apps(abnormal_apps: List[AppSummary],
                           abnormal_apps_file_path: Path = __default_abnormal_apps_file) -> None:
        """
        Saves the abnormal application in a csv file.
        :raises TypeError if abnormal apps is not of type 'List[AppSummary]',
                or if abnormal_apps_file_path is not of type 'pathlib.Path'
        :param abnormal_apps: The list of abnormal apps to store.
        :type abnormal_apps: List[AppSummary]
        :param abnormal_apps_file_path: The file path to save the abnormal apps.
                It defaults to 'paths.APP_ANOM_FILE_PATH'.
        :type abnormal_apps_file_path: pathlib.Path
        """
        if not isinstance(abnormal_apps, list):
            raise TypeError(
                expected_type_but_received_message.format("abnormal_apps", "List[AppSummary]", abnormal_apps)
            )
        if not isinstance(abnormal_apps_file_path, Path):
            raise TypeError(
                expected_type_but_received_message.format(
                    "abnormal_apps_file_path",
                    "pathlib.Path",
                    abnormal_apps_file_path
                )
            )
        if len(abnormal_apps) <= 0:
            return

        data_retrieval_timestamp_name = AppProfileAttribute.data_retrieval_timestamps.name
        abnormal_app_columns = [enum.name for enum in AppSummaryAttribute]
        abnormal_app_columns.remove(AppSummaryAttribute.modelled_app_details.name)
        abnormal_app_columns.remove(AppSummaryAttribute.latest_retrieved_app_details.name)
        abnormal_app_columns.append(data_retrieval_timestamp_name)

        abnormal_apps_parsed = list()
        for abnormal_app in abnormal_apps:
            if not isinstance(abnormal_app, AppSummary):
                raise TypeError(
                    expected_type_but_received_message.format("abnormal_apps", "List[AppSummary]", abnormal_app)
                )
            latest_retrieval_details = abnormal_app.get_latest_retrieved_app_details()
            retrieval_timestamp = latest_retrieval_details[data_retrieval_timestamp_name][0]
            abnormal_app_dict = json.loads(str(abnormal_app))
            abnormal_app_dict[data_retrieval_timestamp_name] = retrieval_timestamp
            abnormal_apps_parsed.append(abnormal_app_dict)

        with_header = not abnormal_apps_file_path.exists()
        data_frame = pandas.DataFrame(abnormal_apps_parsed, columns=abnormal_app_columns)
        data_frame.to_csv(abnormal_apps_file_path, index=False, mode='a+', header=with_header)

    @staticmethod
    def get_saved_abnormal_apps(abnormal_apps_file_path: Path = __default_abnormal_apps_file) \
            -> Dict[str, List[Dict[str, Union[str, list]]]]:
        """
        Retrieved the saved abnormal apps from a csv file.
        :raises TypeError if abnormal_apps_file_path is not of type 'pathlib.Path'
        :param abnormal_apps_file_path: The file path to save the abnormal apps.
                It defaults to 'paths.APP_ANOM_FILE_PATH'.
        :type abnormal_apps_file_path: pathlib.Path
        :return: The saved abnormal app profiles as dictionaries of application names and list of the abnormal values.
                If the file doesn't exist it returns an empty dictionary.
            Format:
                {
                    "app_name": [
                                    {
                                        "error_message": "Some error message",
                                        "risk": "high",
                                        "abnormal_attributes": [],
                                        "data_retrieval_timestamps": "2021-01-31 20:09:03:771116"
                                    }, ...
                                ],
                    ...
                }

        :rtype: Dict[str, List[Dict[str, str]]]
        """

        if not isinstance(abnormal_apps_file_path, Path):
            raise TypeError(
                expected_type_but_received_message.format(
                    "abnormal_apps_file_path",
                    "pathlib.Path",
                    abnormal_apps_file_path
                )
            )

        abnormal_apps_dict = dict()
        data_retrieval_timestamp_name = AppProfileAttribute.data_retrieval_timestamps.name
        abnormal_app_columns = [enum.name for enum in AppSummaryAttribute]
        abnormal_app_columns.remove(AppSummaryAttribute.modelled_app_details.name)
        abnormal_app_columns.remove(AppSummaryAttribute.latest_retrieved_app_details.name)
        abnormal_app_columns.append(data_retrieval_timestamp_name)

        try:
            for batch in pandas.read_csv(abnormal_apps_file_path, chunksize=app_profile_retrieval_chunk_size):
                saved_records = batch.to_dict("records")
                for record in saved_records:
                    app_name = record[AppSummaryAttribute.app_name.name]
                    if app_name not in abnormal_apps_dict:
                        abnormal_apps_dict[app_name] = list()
                    record.pop(AppSummaryAttribute.app_name.name)
                    record[AppSummaryAttribute.abnormal_attributes.name] = \
                        ast.literal_eval(record[AppSummaryAttribute.abnormal_attributes.name])
                    abnormal_apps_dict[app_name].append(record)
        except FileNotFoundError:
            pass

        return abnormal_apps_dict
