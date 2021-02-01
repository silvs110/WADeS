import ast
import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Union

import pandas

import paths
from src.main.common.AppProfile import AppProfile
from src.main.common.AppSummary import AppSummary
from src.main.common.enum.AppProfileAttribute import AppProfileAttribute
from src.main.common.enum.AppSummaryAttribute import AppSummaryAttribute
from src.utils.error_messages import expected_type_but_received_message, file_support_type_error_message
from wades_config import app_profile_retrieval_chunk_size, datetime_format


class AppProfileDataManager:
    __default_app_profiles_file = paths.APP_PROF_DATA_FILE_PATH
    __supported_file_extensions = [".csv"]
    __column_names = [attr.name for attr in AppProfileAttribute]  # Order is important
    __default_retrieval_timestamp_file = paths.RETRIEVAL_TIMESTAMP_FILE_PATH

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
    def save_app_profiles(app_profiles: List[AppProfile], retrieval_timestamp: datetime = None,
                          app_profile_file_path: Union[str, Path] = __default_app_profiles_file,
                          retrieval_timestamp_file_path: Union[str, Path] = __default_retrieval_timestamp_file) -> None:
        """
        Saves the appProfile in the file specified by app_profile_file.
        If no app_profile_file value is provided, it uses the default file, defined in `paths.py`
        :raises TypeError if app_profiles is not of type 'List[AppProfile]',
                or if app_profile_file is not of type 'str' or 'pathlib.Path'.
        :raises ValueError if the file extension of the path is not supported.
        :param app_profiles: The list of AppProfiles to save.
        :type app_profiles: List[AppProfile]
        :param retrieval_timestamp: The latest retrieval timestamp of the AppProfile objects.
        :type retrieval_timestamp: datetime
        :param app_profile_file_path: The path of file to save the application profiles.
        :type app_profile_file_path: Union[str, pathlib.Path]
        :param retrieval_timestamp_file_path: The path of the file to save the retrieval timestamp.
        :type retrieval_timestamp_file_path: Union[str, pathlib.Path]
        """
        if not isinstance(app_profiles, list):
            raise TypeError(expected_type_but_received_message.format("app_profiles", "List[AppProfile]", app_profiles))

        AppProfileDataManager.__validate_path(app_profile_file_path)

        app_profile_list = list()
        for app_profile in app_profiles:

            if not isinstance(app_profile, AppProfile):
                raise TypeError(
                    expected_type_but_received_message.format("app_profiles", "List[AppProfile]", app_profiles))

            app_profile_dict = app_profile.dict_format()
            app_profile_list.append(app_profile_dict)

        data_frame = pandas.DataFrame(app_profile_list, columns=AppProfileDataManager.__column_names)
        data_frame.to_csv(app_profile_file_path, index=False)

        if retrieval_timestamp is not None:
            with open(retrieval_timestamp_file_path, "w") as file:
                file.write(retrieval_timestamp.strftime(datetime_format))

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
        try:
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
        except FileNotFoundError:
            pass

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
    def save_abnormal_apps(abnormal_apps: List[AppSummary]) -> None:
        """
        Saves the abnormal application in a csv file.
        The path of the file the data is stored is defined by 'paths.APP_ANOM_FILE_PATH'.
        :raises TypeError if abnormal apps is not of type 'List[AppSummary]'.
        :param abnormal_apps: The list of abnormal apps to store.
        :type abnormal_apps: List[AppSummary]
        """
        if not isinstance(abnormal_apps, list):
            raise TypeError(
                expected_type_but_received_message.format("abnormal_apps", "List[AppSummary]", abnormal_apps)
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

        with_header = False if paths.APP_ANOM_FILE_PATH.exists() else True
        data_frame = pandas.DataFrame(abnormal_apps_parsed, columns=abnormal_app_columns)
        data_frame.to_csv(paths.APP_ANOM_FILE_PATH, index=False, mode='a+', header=with_header)

    @staticmethod
    def get_saved_abnormal_apps() -> Dict[str, List[Dict[str, str]]]:
        """
        Retrieved the saved abnormal apps from the path defined in 'paths.APP_ANOM_FILE_PATH'.
        :return: The saved abnormal app profiles as dictionaries of application names and list of the abnormal values.
            Format:
                {
                    "app_name": [
                                    {
                                        "error_message": "Some error message",
                                        "risk": "high",
                                        "abnormal_attributes": "[]",
                                        "data_retrieval_timestamps": "2021-01-31 20:09:03:771116"
                                    }, ...
                                ],
                    ...
                }
            Note: The values in the dictionaries stored in the list will be parsed into their correct type, however,
            as it is not currently required to do so, it will be left as strings.
        :rtype: Dict[str, List[Dict[str, str]]]
        """
        abnormal_apps_dict = dict()
        data_retrieval_timestamp_name = AppProfileAttribute.data_retrieval_timestamps.name
        abnormal_app_columns = [enum.name for enum in AppSummaryAttribute]
        abnormal_app_columns.remove(AppSummaryAttribute.modelled_app_details.name)
        abnormal_app_columns.remove(AppSummaryAttribute.latest_retrieved_app_details.name)
        abnormal_app_columns.append(data_retrieval_timestamp_name)

        try:
            for batch in pandas.read_csv(paths.APP_ANOM_FILE_PATH, chunksize=app_profile_retrieval_chunk_size):
                saved_records = batch.to_dict("records")
                for record in saved_records:
                    app_name = record[AppSummaryAttribute.app_name.name]
                    if app_name not in abnormal_apps_dict:
                        abnormal_apps_dict[app_name] = list()
                    record.pop(AppSummaryAttribute.app_name.name)
                    abnormal_apps_dict[app_name].append(record)
        except FileNotFoundError:
            pass

        return abnormal_apps_dict
