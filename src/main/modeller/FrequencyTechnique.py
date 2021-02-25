from typing import List, Union, Tuple, Set

import numpy

import wades_config
from src.main.common.AppProfile import AppProfile
from src.main.common.enum.AppProfileAttribute import AppProfileAttribute
from src.main.common.AppSummary import AppSummary
from src.main.common.RangeKeyDict import RangeKeyDict
from src.main.common.enum.RiskLevel import RiskLevel
from src.utils.error_messages import anomaly_range_percent_not_in_range, expected_type_but_received_message


class FrequencyTechnique:

    def __init__(self, min_number_count_non_anomalous: int = 5) -> None:
        """
        Initializes this class.
        :raises TypeError if min_number_count_non_anomalous is not of type 'int'.
        :raises ValueError if min_number_count_non_anomalous is less than 0.
        :param min_number_count_non_anomalous: The minimum number of data points in the same bin as the 'anomalous'
            point so as to not consider it a high risk anomaly.
        :type min_number_count_non_anomalous: int
        """

        if not isinstance(min_number_count_non_anomalous, int):
            raise TypeError(
                expected_type_but_received_message.format(
                    "min_number_count_non_anomalous",
                    "int",
                    min_number_count_non_anomalous
                )
            )

        if min_number_count_non_anomalous < 0:
            raise ValueError(anomaly_range_percent_not_in_range.format(0, min_number_count_non_anomalous))

        # This variable stores the minimum number of data points in the same bin as the detected 'anomalous' point.
        # It is useful in case of modelling new data and sets how strict does the technique can be.
        self.__min_count_non_anomalous = min_number_count_non_anomalous

    def get_minimum_count_non_anomalous(self) -> int:
        """
        Gets the value of min_count_non_anomalous.
        This variable stores the minimum number of data points in the same bin as the detected 'anomalous' point.
        It is useful in case of modelling new data and sets how strict does the technique can be.
        :return: minimum count for a point inside a bin to be considered non anomalous.
        :rtype: int
        """
        return self.__min_count_non_anomalous

    def set_minimum_count_non_anomalous(self, new_value: int) -> None:
        """
        Sets the minimum number of data points in the same bin as the 'anomalous' point so as to not consider it a
        high risk anomaly.
        :raises TypeError if new_value is not of type 'int'.
        :raises ValueError if new_value is less than 0.
        :param new_value: The new value of min_count_non_anomalous.
        :type new_value: int
        """

        if not isinstance(new_value, int):
            raise TypeError(
                expected_type_but_received_message.format(
                    "new_value",
                    "int",
                    new_value
                )
            )

        if new_value < 0:
            raise ValueError(anomaly_range_percent_not_in_range.format(0, new_value))
        self.__min_count_non_anomalous = new_value

    # Should be a callable technique
    def __call__(self, data: List[AppProfile]) -> List[AppSummary]:
        """
        Models the list of AppProfiles.
        :raises TypeError if data is not of type List[AppProfile].
        :param data: The list of AppProfiles to model.
        :type data: List[AppProfile]
        :return: A list of modelled AppProfiles in the form of AppSummary objects.
        :rtype: List[AppSummary]
        """

        if not isinstance(data, list):
            raise TypeError(
                expected_type_but_received_message.format(
                    "data",
                    " List[AppProfile]",
                    data
                )
            )

        modelled_apps = list()

        for app_profile in data:
            app_summary = self.__frequency_modelling_app(app_profile=app_profile)
            modelled_apps.append(app_summary)

        return modelled_apps

    def __frequency_modelling_app(self, app_profile: AppProfile) -> AppSummary:
        """
        Create the frequency model for each attribute in AppProfile. The following attributes are modelled:
        - __memory_usages
        - __cpu_percent_usages
        - __open_files
        - __data_retrieval_timestamp
        - __child_processes_count
        - __users
        :raises TypeError if app_profile is not an instance of 'AppProfile'.
        :param app_profile: The application to model.
        :type app_profile: AppProfile
        :return: the modelled application as an AppSummary instance.
        :rtype: AppSummary
        """
        if not isinstance(app_profile, AppProfile):
            raise TypeError(
                expected_type_but_received_message.format(
                    "app_profile",
                    "AppProfile",
                    app_profile
                )
            )

        numeric_attribute_names = {AppProfileAttribute.memory_infos.name, AppProfileAttribute.cpu_percents.name,
                                   AppProfileAttribute.children_counts.name, AppProfileAttribute.threads_numbers.name,
                                   AppProfileAttribute.connections_numbers.name}
        error_message = None
        max_risk_level = RiskLevel.none
        anomalous_attrs = set()

        normalized_app_profile_data = app_profile.get_previously_retrieved_data()
        latest_app_profile_data = app_profile.get_latest_retrieved_data()

        if wades_config.is_modelling:

            # Numeric data
            is_anomalous_numeric, numeric_max_risk_level, anomalous_attrs = \
                self.__detect_anomalies_in_numeric_attributes(normal_app_profile_data=normalized_app_profile_data,
                                                              latest_app_profile_data=latest_app_profile_data,
                                                              numeric_attribute_names=numeric_attribute_names)
            # Non-numeric data
            is_anomalous_non_numeric, non_numeric_max_risk_level, non_numeric_anomalous_attrs = \
                FrequencyTechnique.__detect_anomalies_in_non_numeric_attributes(
                    normalized_app_profile_data=normalized_app_profile_data,
                    latest_app_profile_data=latest_app_profile_data)

            # Prepare data to convert it into an AppSummary object.
            max_risk_level = max(numeric_max_risk_level, non_numeric_max_risk_level)
            anomalous_attrs.update(non_numeric_anomalous_attrs)

            if is_anomalous_non_numeric or is_anomalous_numeric:
                error_message = wades_config.anomaly_detected_message
        app_summary = AppSummary(app_name=app_profile.get_application_name(),
                                 error_message=error_message,
                                 risk=max_risk_level,
                                 abnormal_attrs=anomalous_attrs,
                                 latest_retrieved_app_details=latest_app_profile_data,
                                 modelled_app_details=latest_app_profile_data)
        return app_summary

    def __detect_anomalies_in_numeric_attributes(self, normal_app_profile_data: dict, latest_app_profile_data: dict,
                                                 numeric_attribute_names: Set[str]) -> Tuple[bool, RiskLevel, Set[str]]:
        """
        Detects the anomalies for all numeric attributes.
        :raises TypeError if normal_app_profile_data or latest_app_profile_data are not of type 'dict',
                or if numeric_attribute_names is not of type 'Set[str]'.
        :param normal_app_profile_data: The normalized application profile data as a dictionary.
                For more info about the format: 'src.main.common.AppProfile.AppProfile.get_previously_retrieved_data'
        :type normal_app_profile_data: dict
        :param latest_app_profile_data: The latest application profile data as a dictionary.
                For more info about the format: 'src.main.common.AppProfile.AppProfile.get_latest_retrieved_data'
        :type latest_app_profile_data: dict
        :param numeric_attribute_names: The numeric attribute names.
        :type numeric_attribute_names: numeric_attribute_names: Set[str]
        :return: A tuple with the values of the anomaly detection for all numeric attributes along with the maximum
                risk level found.
        :rtype: Tuple[bool, RiskLevel, Set[str]]
        """

        # Input Validation
        if not isinstance(normal_app_profile_data, dict):
            raise TypeError(
                expected_type_but_received_message.format(
                    "normal_app_profile_data",
                    "dict",
                    normal_app_profile_data
                )
            )

        if not isinstance(latest_app_profile_data, dict):
            raise TypeError(
                expected_type_but_received_message.format(
                    "latest_app_profile_data",
                    "dict",
                    latest_app_profile_data
                )
            )

        if not isinstance(numeric_attribute_names, set):
            raise TypeError(
                expected_type_but_received_message.format(
                    "numeric_attribute_names",
                    "Set[str]",
                    numeric_attribute_names
                )
            )

        risk_levels = set()
        anomalous_attrs = set()
        for numeric_attribute_name in numeric_attribute_names:
            normal_attribute_values = normal_app_profile_data[numeric_attribute_name]
            latest_attribute_values = latest_app_profile_data[numeric_attribute_name]

            anomaly_found, risk_level = self.__detect_anomalies_in_numeric_attribute(
                previous_attribute_data=normal_attribute_values, latest_attribute_data=latest_attribute_values)
            risk_levels.add(risk_level)
            if anomaly_found:
                anomalous_attrs.add(numeric_attribute_name)

        anomaly = len(anomalous_attrs) > 0
        max_risk_level = max(risk_levels)

        return anomaly, max_risk_level, anomalous_attrs

    @staticmethod
    def __detect_anomalies_in_non_numeric_attributes(normalized_app_profile_data: dict,
                                                     latest_app_profile_data: dict) \
            -> Tuple[bool, RiskLevel, Set[str]]:
        """
        Detects anomalies in non numeric attributes. Currently it only checks 'users' and 'opened_files' attributes.
        :raises TypeError if normalized_app_profile_data or latest_app_profile_data are not of type 'dict'.
        :param normalized_app_profile_data: The normalized application profile data as a dictionary.
                For more info about the format: 'src.main.common.AppProfile.AppProfile.get_previously_retrieved_data'
        :type normalized_app_profile_data: dict
        :param latest_app_profile_data: The latest application profile data as a dictionary.
                For more info about the format: 'src.main.common.AppProfile.AppProfile.get_latest_retrieved_data'
        :type latest_app_profile_data: dict
        :return: A tuple with the values of the anomaly detection for all non-numeric attributes along with
                the max risk level found.
        :rtype: Tuple[bool, RiskLevel, Set[str]]
        """

        # Input Validation
        if not isinstance(normalized_app_profile_data, dict):
            raise TypeError(
                expected_type_but_received_message.format(
                    "normalized_app_profile_data",
                    "dict",
                    normalized_app_profile_data
                )
            )

        if not isinstance(latest_app_profile_data, dict):
            raise TypeError(
                expected_type_but_received_message.format(
                    "latest_app_profile_data",
                    "dict",
                    latest_app_profile_data
                )
            )

        normalized_users = normalized_app_profile_data[AppProfileAttribute.usernames.name]
        last_retrieved_users = latest_app_profile_data[AppProfileAttribute.usernames.name]

        is_user_attr_anomalous, user_attr_risk_level, anomalous_users = \
            FrequencyTechnique.__detect_anomalies_in_non_numeric_attribute_with_whitelisting(
                normalized_attribute_data=normalized_users, last_retrieved_attribute_data=last_retrieved_users)
        non_numeric_anomalous_attrs = {AppProfileAttribute.usernames.name} if is_user_attr_anomalous else set()

        # Get opened files info and parse it into appropriate format
        normalized_files = normalized_app_profile_data[AppProfileAttribute.opened_files.name]
        normalized_files_flat = list()
        for files in normalized_files:
            normalized_files_flat.extend(files)

        last_retrieved_files = latest_app_profile_data[AppProfileAttribute.opened_files.name]
        last_retrieved_files_flat = list()
        for files in last_retrieved_files:
            last_retrieved_files_flat.extend(files)

        is_files_anomalous_whitelist, files_whitelist_risk_level, anomalous_file_whitelist = \
            FrequencyTechnique.__detect_anomalies_in_non_numeric_attribute_with_whitelisting(
                normalized_attribute_data=normalized_files_flat,
                last_retrieved_attribute_data=last_retrieved_files_flat)

        is_files_anomalous_blacklist, files_blacklist_risk_level, anomalous_file_blacklist = \
            FrequencyTechnique.__detect_anomalies_in_non_numeric_attribute_with_blacklisting(
                normalized_attribute_data=normalized_files_flat,
                last_retrieved_attribute_data=last_retrieved_files_flat,
                blacklisted_values=wades_config.prohibited_files)

        if is_files_anomalous_blacklist or is_files_anomalous_whitelist:
            non_numeric_anomalous_attrs.add(AppProfileAttribute.opened_files.name)

        is_anomalous = is_user_attr_anomalous or is_files_anomalous_whitelist or is_files_anomalous_blacklist
        files_max_risk = max([files_blacklist_risk_level, files_whitelist_risk_level, user_attr_risk_level])

        return is_anomalous, files_max_risk, non_numeric_anomalous_attrs

    @staticmethod
    def __build_dict_frequency(data: List[Union[int, float]]) -> RangeKeyDict:
        """
        Creates the frequency model as a dictionary. It uses Freedman–Diaconis rule.
        :raises TypeError if data is not of type 'List[Union[int, float]]'.
        :param data: The data to model.
        :type data: List[Union[int, float]]
        :return: The frequency model as a dictionary.
        :rtype Dict[range, int]
        """

        if not isinstance(data, list):
            raise TypeError(
                expected_type_but_received_message.format(
                    "data",
                    "List[Union[int, float]]",
                    data
                )
            )

        frequency_model = RangeKeyDict()
        data_count_in_bins, raw_bin_edges = numpy.histogram(data, bins='fd')
        if len(raw_bin_edges) == 0:
            return frequency_model
        initial_range = raw_bin_edges[0]
        bin_edges = raw_bin_edges[1:]

        for index in range(0, len(data_count_in_bins)):
            bin_edge = bin_edges[index]
            frequency_model[(initial_range, bin_edge)] = data_count_in_bins[index]
            initial_range = bin_edge

        return frequency_model

    # noinspection DuplicatedCode
    def __detect_anomalies_in_numeric_attribute(self, previous_attribute_data: List[Union[int, float]],
                                                latest_attribute_data: List[Union[int, float]]) -> \
            Tuple[bool, RiskLevel]:
        """
        Detect anomalies in numeric data and then assigns it a risk level.
        The risk level assigned depends on the following criteria:
        * The distance of the new data point to the median. The farther it is the greater the risk.
        * If the new data point is in the upper outlier, then it will likely be assigned a high risk.
        * If it's in lower outlier, then it is medium risk category.
        * If the new data point belongs to a bin that has more than
            a specified number of points (min_count_non_anomalous), its risk level lowers
            by 1 (unless it is in the low category).
        * Only if there are no anomalies found, the risk_level assigned is none.
        :raises TypeError if previous_attribute_data or latest_attribute_data are not of type 'List[Union[int, float]]'.
        :param previous_attribute_data: The numeric data used to create the normalized model.
        :type previous_attribute_data: List[Union[int, float]]
        :param latest_attribute_data: The numeric data to investigate.
        :type latest_attribute_data: List[Union[int, float]]
        :return: A tuple with the values of the anomaly detection along with the risk level
            associated to the anomaly found.
        :rtype: Tuple[bool, RiskLevel]
        """

        # Input Validation
        if not isinstance(previous_attribute_data, list):
            raise TypeError(
                expected_type_but_received_message.format(
                    "previous_attribute_data",
                    "List[Union[int, float]]",
                    previous_attribute_data
                )
            )

        if not isinstance(latest_attribute_data, list):
            raise TypeError(
                expected_type_but_received_message.format(
                    "latest_attribute_data",
                    "List[Union[int, float]]",
                    latest_attribute_data
                )
            )
        if len(previous_attribute_data) < wades_config.minimum_retrieval_size_for_modelling:
            return False, RiskLevel.none
        attribute_model = FrequencyTechnique.__build_dict_frequency(data=previous_attribute_data)

        q1, q3 = numpy.percentile(previous_attribute_data, [25, 75])
        iqr = q3 - q1

        lower_outlier = q1 - (1.5 * iqr)
        upper_outlier = q3 + (1.5 * iqr)
        lowest_point = min(previous_attribute_data)
        highest_point = max(previous_attribute_data)

        for new_point in latest_attribute_data:
            bin_count = attribute_model[new_point]
            if new_point < lower_outlier:

                risk_level = RiskLevel.medium
                distance_to_lowest_point = new_point - lowest_point
                distance_to_outlier = lower_outlier - new_point
                # If distance_to_lowest point is negative, the new point is lesser than the recorded lowest point.
                if lower_outlier > lowest_point \
                        and distance_to_lowest_point > 0 \
                        and distance_to_outlier < distance_to_lowest_point:
                    risk_level -= 1

                if bin_count is not None \
                        and bin_count > self.__min_count_non_anomalous \
                        and risk_level > risk_level.low:
                    risk_level -= 1
                return True, risk_level

            elif new_point > upper_outlier:
                risk_level = RiskLevel.high
                distance_to_highest_point = highest_point - new_point
                distance_to_outlier = new_point - upper_outlier
                # If the distance_to_highest_point is negative, the new point is greater than the recorded highest point
                if upper_outlier < highest_point \
                        and distance_to_highest_point > 0 \
                        and distance_to_outlier < distance_to_highest_point:

                    risk_level -= 1

                if bin_count is not None \
                        and bin_count > self.__min_count_non_anomalous \
                        and risk_level > risk_level.low:
                    risk_level -= 1

                return True, risk_level

        return False, RiskLevel.none

    @staticmethod
    def __detect_anomalies_in_non_numeric_attribute_with_whitelisting(normalized_attribute_data: List[str],
                                                                      last_retrieved_attribute_data: List[str]) -> \
            Tuple[bool, RiskLevel, Set[str]]:
        """
        Detects anomalies by using a whitelist method.
        :raises TypeError if normalized_attribute_data or last_retrieved_attribute_data are not of type 'List[str]'.
        :param normalized_attribute_data: The normalized attribute data.
        :type normalized_attribute_data: List[str]
        :param last_retrieved_attribute_data: The latest retrieved data.
        :type last_retrieved_attribute_data: List[str]
        :return: The results of the anomaly detection through whitelisting. The result is in the following format:
            (anomaly_found, risk_level, anomalous_values)
                anomaly_found: Flag for if an anomaly has been found.
                risk_level: The risk level associated to the anomaly. For this, the risk level is medium risk.
                anomalous_values: Provides detailed information of the anomalous values.
        :rtype: Tuple[bool, RiskLevel, Set[str]]
        """
        # Input Validation
        if not isinstance(normalized_attribute_data, list):
            raise TypeError(
                expected_type_but_received_message.format(
                    "normalized_attribute_data",
                    "List[str]",
                    normalized_attribute_data
                )
            )

        if not isinstance(last_retrieved_attribute_data, list):
            raise TypeError(
                expected_type_but_received_message.format(
                    "last_retrieved_attribute_data",
                    "List[str]",
                    last_retrieved_attribute_data
                )
            )

        anomaly_found = False
        risk_level = RiskLevel.none

        # when there is not enough data
        if len(normalized_attribute_data) < wades_config.minimum_retrieval_size_for_modelling:
            return False, RiskLevel.none, set()

        last_retrieved_data_set = set(last_retrieved_attribute_data)

        new_data_accessed = last_retrieved_data_set.difference(normalized_attribute_data)
        if len(new_data_accessed) > 0:
            anomaly_found = True
            risk_level = RiskLevel.medium

        return anomaly_found, risk_level, new_data_accessed

    @staticmethod
    def __detect_anomalies_in_non_numeric_attribute_with_blacklisting(normalized_attribute_data: List[str],
                                                                      last_retrieved_attribute_data: List[str],
                                                                      blacklisted_values: Set[str]) \
            -> Tuple[bool, RiskLevel, Set[str]]:
        """
        Detects anomalies by using blacklisting approach.
        :raises TypeError if normalized_attribute_data or last_retrieved_attribute_data are not of type 'List[str]',
                or if blacklisted_values is not of type 'Set[str]'
        :param normalized_attribute_data: The normalized attribute data.
        :type normalized_attribute_data: List[str]
        :param last_retrieved_attribute_data: The latest retrieved data.
        :type last_retrieved_attribute_data: List[str]
        :param blacklisted_values: The blacklisted values.
        :type blacklisted_values: Set[str]
        :return: The results of the anomaly detection through whitelisting.
            If a blacklisted value has been accessed before, it is not considered an anomaly if it is accessed again.
            The result is in the following format:
                (anomaly_found, risk_level, anomalous_values)
                    anomaly_found: Flag for if an anomaly has been found.
                    risk_level: The risk level associated to the anomaly. For this, the risk level is high risk.
                    anomalous_values: Provides detailed information of the anomalous values.
        :rtype: Tuple[bool, RiskLevel, Set[str]]
        """

        # Input Validation

        if not isinstance(normalized_attribute_data, list):
            raise TypeError(
                expected_type_but_received_message.format(
                    "normalized_attribute_data",
                    "List[str]",
                    normalized_attribute_data
                )
            )

        if not isinstance(blacklisted_values, set):
            raise TypeError(
                expected_type_but_received_message.format(
                    "blacklisted_values",
                    "Set[str]",
                    blacklisted_values
                )
            )
        if not isinstance(last_retrieved_attribute_data, list):
            raise TypeError(
                expected_type_but_received_message.format(
                    "last_retrieved_attribute_data",
                    "List[str]",
                    last_retrieved_attribute_data
                )
            )

        anomaly_found = False
        risk_level = RiskLevel.none

        normalized_attribute_data_set = set(normalized_attribute_data)
        previously_accessed_blacklisted_values = normalized_attribute_data_set.intersection(blacklisted_values)
        # Get the blacklisted data that haven't been accessed before.
        not_previously_accessed_blacklisted_values = \
            blacklisted_values.difference(previously_accessed_blacklisted_values)
        recently_accessed_blacklisted_values = not_previously_accessed_blacklisted_values.intersection(
            last_retrieved_attribute_data)
        if len(recently_accessed_blacklisted_values) > 0:
            anomaly_found = True
            risk_level = RiskLevel.high

        return anomaly_found, risk_level, recently_accessed_blacklisted_values
