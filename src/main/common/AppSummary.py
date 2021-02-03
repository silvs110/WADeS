import copy
import json
from typing import Union, Set

from src.main.common.enum.AppProfileAttribute import AppProfileAttribute
from src.main.common.enum.AppSummaryAttribute import AppSummaryAttribute
from src.main.common.enum.RiskLevel import RiskLevel


class AppSummary:
    def __init__(self, app_name: str, error_message: Union[str, None], risk: RiskLevel, abnormal_attrs: Set[str],
                 latest_retrieved_app_details: dict, modelled_app_details: dict) -> None:
        """
        Constructor for the AppSummary class.
        :param app_name: The name of the application.
        :type app_name: str
        :param error_message: The error message associated to the anomaly.
        :type error_message: str
        :param risk: The risk level associated to the anomaly.
        :type risk: RiskLevel
        :param abnormal_attrs: The collection of abnormal attributes.
        :type abnormal_attrs: Set[str]
        :param latest_retrieved_app_details: The latest retrieved data for a specific app profile.
        :type latest_retrieved_app_details: dict
        :param modelled_app_details: The modelled data of a specific app_profile.
        :type modelled_app_details: dict
        """
        self.__app_name = app_name
        self.__error_message = error_message
        self.__risk = risk
        self.__abnormal_attributes = abnormal_attrs
        self.__latest_retrieved_app_details = latest_retrieved_app_details
        self.__modelled_app_details = modelled_app_details

    def get_app_name(self) -> str:
        """
        Gets the name of the application.
        :return: The name of the application.
        :rtype: str
        """
        return self.__app_name

    def get_error_message(self) -> Union[str, None]:
        """
        Gets the error message associated to the modelled application.
        :return: The error message associated to this application model.
        :rtype: Union[str, None]
        """
        return self.__error_message

    def get_risk_level(self) -> RiskLevel:
        """
        Gets the anomaly risk level. If multiple anomalies are found while modelling the application,
        this returns the highest risk level.
        :return: The risk level associated to the anomaly found.
        :rtype: RiskLevel
        """
        return self.__risk

    def get_abnormal_attrs(self) -> Set[str]:
        """
        Gets the name of the abnormal attributes.
        :return: The collection of the anomalous attributes.
        :rtype: Set[str]
        """
        return copy.deepcopy(self.__abnormal_attributes)

    def get_latest_retrieved_app_details(self) -> dict:
        """
        Gets the latest retrieved data for this application.
        Format:
            {
                app_name: "Some name",
                data_retrieval_timestamps: [timestamp_1, timestamp_2, ...],
                usernames: [user_1, user_2, ...]
                memory_infos: [2342, 23215, 31573, ...],
                opened_files:[[path_1, path_2, ...], [path_45, ...], ...],
                cpu_percents: [0.2, 13.9, ...],
                children_counts: [1, 5, 0, 4, ...],
                threads_numbers:[0, 1, 3, 9, ...]
            }
        :return: The latest retrieved data.
        :rtype: dict
        """
        return copy.deepcopy(self.__latest_retrieved_app_details)

    def get_modelled_app_details(self) -> dict:
        """
        Gets the modelled data for this application.
        Format:
            {
                app_name: "Some name",
                data_retrieval_timestamps: [timestamp_1, timestamp_2, ...],
                usernames: [user_1, user_2, ...]
                memory_infos: [2342, 23215, 31573, ...],
                opened_files:[[path_1, path_2, ...], [path_45, ...], ...],
                cpu_percents: [0.2, 13.9, ...],
                children_counts: [1, 5, 0, 4, ...],
                threads_numbers:[0, 1, 3, 9, ...]
            }
        :return: The latest retrieved data.
        :rtype: dict
        """
        return copy.deepcopy(self.__modelled_app_details)

    def dict_format(self) -> dict:
        """
        Get the AppSummary object as a dictionary.
        :return: The AppSummary object as a dictionary.
            Format:
            {
                app_name: "Some name",
                risk: risk_level,
                error_message: some_message,
                abnormal_attributes: abnormal_attrs,
                modelled_app_details: modelled_app_info,
                latest_retrieved_app_details: latest_retrieved_app_data
            }
            Note: All keys uses the enum's names in AppSummaryAttribute.
        :rtype: dict
        """
        return {
            AppSummaryAttribute.app_name.name: self.__app_name,
            AppSummaryAttribute.risk.name: self.__risk,
            AppSummaryAttribute.error_message.name: self.__error_message,
            AppSummaryAttribute.abnormal_attributes.name: copy.deepcopy(self.__abnormal_attributes),
            AppSummaryAttribute.modelled_app_details.name: copy.deepcopy(self.__modelled_app_details),
            AppSummaryAttribute.latest_retrieved_app_details.name: copy.deepcopy(self.__latest_retrieved_app_details)
        }

    def __str__(self) -> str:
        """
        Overloads the str method to return a str representation of this object.
        :return: The str representation of this object.
        :rtype: str
        """
        latest_retrieved_app_details_copy = copy.deepcopy(self.__latest_retrieved_app_details)
        latest_retrieved_app_details_copy[AppProfileAttribute.opened_files.name] = [
            opened_file
            for opened_files_batch in latest_retrieved_app_details_copy[AppProfileAttribute.opened_files.name]
            for opened_file in opened_files_batch
        ]
        app_values = {
            AppSummaryAttribute.app_name.name: self.__app_name,
            AppSummaryAttribute.risk.name: self.__risk.name,
            AppSummaryAttribute.error_message.name: self.__error_message,
            AppSummaryAttribute.abnormal_attributes.name: list(self.__abnormal_attributes)
        }
        return json.dumps(app_values)
