import copy
import datetime
import time
import psutil

import wades_config
from src.main.common.AppProfileAttribute import AppProfileAttribute
from src.utils.error_messages import expected_type_but_received_message, expected_value_but_received_message
from typing import Union


class AppProfile:
    def __init__(self, application_name: str) -> None:
        """
        Abstracts the Application Profile past and current usages.
        :raises TypeError if application_name is not of type 'str'.
        :param application_name: the name of the application.
        :type application_name: str
        """
        if not (isinstance(application_name, str)):
            raise TypeError(expected_type_but_received_message.format("application_name", "str", application_name))

        self.__object_creation_timestamp = datetime.datetime.now()
        self.__name = application_name
        self.__memory_usages = list()  # this is in bytes
        self.__cpu_percent_usages = list()
        self.__open_files = list()
        self.__data_retrieval_timestamp = list()
        self.__child_processes_count = list()
        self.__users = list()

    def get_application_name(self) -> str:
        """
        Gets the name of the application.
        :return: The name of the application.
        :rtype: str
        """
        return self.__name

    def get_object_creation_timestamp(self) -> datetime.datetime:
        """
        Gets the timestamp this object was created.
        :return: The timestamp this object was created.
        :rtype: datetime.datetime
        """
        return self.__object_creation_timestamp

    def get_memory_usages(self) -> list:
        """
        Gets the memory usages for this application. It will return all recorded memory usages.
        :return: The past memory usages for this application.
        :rtype: list
        """
        return copy.deepcopy(self.__memory_usages)

    def get_open_files(self) -> list:
        """
        Gets the dictionary of opened files for this application.
        Format:
                [[path_1, path_2, ...], [path_45, ...], ...]
        :return: A dictionary of opened files and the permissions.
        :rtype: list
        """
        return copy.deepcopy(self.__open_files)

    def get_data_retrieval_timestamp(self) -> list:
        """
        Gets a list of all the retrieval times.
        :return: A list of retrieval times.
        :rtype: list
        """
        return copy.deepcopy(self.__data_retrieval_timestamp)

    def get_child_processes_count(self) -> list:
        """
        Gets a history of all the child processes count.
        :return: A list of all the child processes count.
        :rtype: list
        """
        return copy.deepcopy(self.__child_processes_count)

    def get_users(self) -> list:
        """
        Gets the users that have run this application.
        :return: The collection of users that have run this application.
        :rtype: list
        """
        return copy.deepcopy(self.__users)

    def get_cpu_percentages(self) -> list:
        """
        Gets the history of cpu usages for this application.
        :return: The history of the cpu usages for this application.
        :rtype: list
        """
        return copy.deepcopy(self.__cpu_percent_usages)

    def __str__(self) -> str:
        """
        Overload of the method __str__ to display the information about the application in a more readable format.
        :return: The information about the application in a more readable format.
        :rtype: str
        """
        return f"Application: {self.__name}"

    def __eq__(self, other: Union["AppProfile", str]) -> bool:
        """
        Overloads the == operator. Two applications are equal if they have the same name.
        :param other: The other application to compare.
        :type other: Union["Application", str]
        :return: True if the two applications have the same name, False otherwise.
        :rtype: bool
        """
        if not isinstance(other, (AppProfile, str)):
            return False
        elif isinstance(other, str):
            return self.__name == other
        return self.__name == other.__name

    def __ne__(self, other: Union["AppProfile", str]) -> bool:
        """
        Overloads the != operator. Two applications are equal if they have the same name.
        :param other: The other application to compare.
        :type other: Union["Application", str]
        :return: True if the two applications don't have the same name, False otherwise.
        :rtype: bool
        """
        return not self.__eq__(other=other)

    def add_new_information_from_process_object(self, process: psutil.Process,
                                                data_retrieval_timestamp: datetime.datetime) -> None:
        """
        Adds the new information about the process to the application profile.
        This should be mainly used for applications with only one process.
        :raises TypeError if process is not of type psutil.Process or data_retrieval_timestamp is not of type
            datetime.datetime.
        :raises ValueError if data_retrieval_timestamp is newer than current time.
        :param process: Information about the specific process.
        :type process: psutil.Process
        :param data_retrieval_timestamp: The time the data was retrieved.
        :type data_retrieval_timestamp: datetime.datetime
        """
        if not (isinstance(process, psutil.Process)):
            raise TypeError(expected_type_but_received_message.format("process", "psutil.Process", process))
        if not (isinstance(data_retrieval_timestamp, datetime.datetime)):
            raise TypeError(expected_type_but_received_message.format("data_retrieval_timestamp", "datetime.datetime",
                                                                      data_retrieval_timestamp))
        if data_retrieval_timestamp.replace(tzinfo=None) > datetime.datetime.now():
            raise ValueError("Argument data_retrieval_timestamp cannot be newer than current time. Value receive: {}"
                             .format(data_retrieval_timestamp))

        # Get info from the process object. One of the following calls may raise an Error (OS, AccessDenied, etc).
        open_files = process.open_files()
        memory_info = process.memory_info()
        child_process_count = len(process.children())
        username = process.username()
        process.cpu_percent()

        time.sleep(0.1)  # wait for cpu_percent to return a meaningful value.
        cpu_percentage = process.cpu_percent()

        self.add_open_files(open_files=open_files, data_retrieval_timestamp=data_retrieval_timestamp)
        self.__memory_usages.append(memory_info.rss)
        self.__data_retrieval_timestamp.append(data_retrieval_timestamp)
        self.__child_processes_count.append(child_process_count)
        self.__users.extend(username)
        self.__cpu_percent_usages.append(cpu_percentage)

    def add_new_information(self, memory_usage: int, child_processes_count: int, users: list, open_files: list,
                            cpu_percentage: float, data_retrieval_timestamp: datetime.datetime) -> None:
        """
        Adds new information about this application. Adds for a specific process associated to the application.
        :raises TypeError if one of the following criteria is met:
            - memory_usage or child_processes_count is not of type 'int'
            - users is not of type 'set'
            - open_files is not of type 'list'
            - cpu_percentage is not of type 'float'
            - data_retrieval_timestamp is not of type 'datetime.datetime'
        :raises ValueError if either memory_usage, child_processes_count or cpu_percentage has negative value,
                or if data_retrieval_timestamp is newer than current time.
        :param memory_usage: The memory usage of this application.
        :type memory_usage: int
        :param child_processes_count: The number of child process registered at the moment.
        :type child_processes_count: int
        :param users: The users that are running this application.
        :type users: list
        :param open_files: The open files to add.
        :type open_files: list
        :param cpu_percentage: Current CPU usage for this application.
        :type cpu_percentage: float
        :param data_retrieval_timestamp: The time the data was retrieved.
        :type data_retrieval_timestamp: datetime.datetime
        """
        if not isinstance(memory_usage, int):
            raise TypeError(expected_type_but_received_message.format("memory_usages", "int", memory_usage))
        if not isinstance(child_processes_count, int):
            raise TypeError(
                expected_type_but_received_message.format("child_processes_count", "int", child_processes_count))
        if not isinstance(users, list):
            raise TypeError(expected_type_but_received_message.format("users", "list", users))
        if not isinstance(open_files, list):
            raise TypeError(expected_type_but_received_message.format("open_files", "list", open_files))
        if not isinstance(cpu_percentage, float):
            raise TypeError(expected_type_but_received_message.format("cpu_percentage", "float", cpu_percentage))
        if not (isinstance(data_retrieval_timestamp, datetime.datetime)):
            raise TypeError(expected_type_but_received_message.format("data_retrieval_timestamp", "datetime.datetime",
                                                                      data_retrieval_timestamp))
        if memory_usage < 0 or child_processes_count < 0 or cpu_percentage < 0:
            raise ValueError(
                "Arguments memory_usage, child_processes_count and cpu_percentage cannot have negative value, "
                "but received [%s, %s, %s]".format(
                    memory_usage, child_processes_count, cpu_percentage))
        if data_retrieval_timestamp.replace(tzinfo=None) > datetime.datetime.now():
            raise ValueError("Argument data_retrieval_timestamp cannot be newer than current time. Value receive: %s"
                             .format(data_retrieval_timestamp))

        self.add_open_files(open_files=open_files, data_retrieval_timestamp=data_retrieval_timestamp)
        self.__memory_usages.append(memory_usage)
        self.__child_processes_count.append(child_processes_count)
        self.__users.extend(users)
        self.__cpu_percent_usages.append(cpu_percentage)
        self.__data_retrieval_timestamp.append(data_retrieval_timestamp)

    def add_open_files(self, open_files: list, data_retrieval_timestamp: datetime.datetime) -> None:
        """
        Adds the open files to the list of open files for this application.
        :raises TypeError if open_files is not of type list,
                or if data_retrieval_timestamp is not of type datetime.datetime.
        :param open_files: The open files to add.
        :type open_files: list
        :param data_retrieval_timestamp: The time the data was retrieved.
        :type data_retrieval_timestamp: datetime.datetime
        """

        if not isinstance(open_files, list):
            raise TypeError(expected_type_but_received_message.format("open_files", "list", open_files))
        if not isinstance(data_retrieval_timestamp, datetime.datetime):
            raise TypeError(expected_type_but_received_message.format("data_retrieval_timestamp", "datetime.datetime",
                                                                      data_retrieval_timestamp))
        last_accessed_files = {open_file.path for open_file in open_files}

        self.__open_files.append(list(last_accessed_files))

    def dict_format(self) -> dict:
        """
        Converts the attributes of this instance of AppProfile to a dict_format object.
        :return: The dict_format object of this instance.
        Format:
            {
                app_name: "Some name",
                date_created_timestamp: "2020-12-12 14:30:32:34.232",
                usernames: [user_1, user_2, ...]
                memory_infos: [2342, 23215, 31573, ...],
                opened_files: [[path_1, path_2, ...], [path_45, ...], ...],
                cpu_percents: [0.2, 13.9, ...],
                children_counts: [1, 5, 0, 4, ...]
                data_retrieval_timestamps: [timestamp_1, timestamp_2, ...]
            }
        All timestamp have 'YYYY-MM-DD HH:MM:SS:microseconds' format.
        :rtype: dict
        """
        str_data_retrieval_timestamps = list()
        for timestamp in self.__data_retrieval_timestamp:
            str_timestamp = timestamp.strftime(wades_config.datetime_format)
            str_data_retrieval_timestamps.append(str_timestamp)
        object_creation_timestamp = self.__object_creation_timestamp.strftime(wades_config.datetime_format)

        app_attrs = {
            AppProfileAttribute.app_name.name: self.__name,
            AppProfileAttribute.date_created_timestamp.name: object_creation_timestamp,
            AppProfileAttribute.memory_infos.name: self.__memory_usages,
            AppProfileAttribute.cpu_percents.name: self.__cpu_percent_usages,
            AppProfileAttribute.opened_files.name: self.__open_files,
            AppProfileAttribute.data_retrieval_timestamps.name: str_data_retrieval_timestamps,
            AppProfileAttribute.children_counts.name: self.__child_processes_count,
            AppProfileAttribute.usernames.name: self.__users
        }

        return app_attrs

    def set_value_from_dict(self, app_profile_dict: dict) -> None:
        """
        Set the value from dict. Any old values will be lost.
        If app_name is passed as a key, that value is ignored.
        :raises TypeError if app_profile_dict is not of type 'dict',
                or if the following values don't match their required type:
            - memory_infos -> List[int]
            - cpu_percent -> List[float]
            - children_count -> List[int]
            - usernames -> List[str]
            - opened_files -> List[List[str]]
        :raises ValueError if app_profile_dict does not have the following keys:
            - app_name
            - date_created_timestamp
            - usernames
            - memory_infos
            - opened_files
            - cpu_percents
            - children_counts
            - data_retrieval_timestamps
        :param app_profile_dict: the new values of the application profile.
        Format:
            {
                app_name: "Some name",
                date_created_timestamp: "2020-12-12 14:30:32:34.232",
                usernames: [user_1, user_2, ...]
                memory_infos: [2342, 23215, 31573, ...],
                opened_files: [[path_1, path_2, ...], [path_45, ...], ...],
                cpu_percents: [0.2, 13.9, ...],
                children_counts: [1, 5, 0, 4, ...]
                data_retrieval_timestamps: [timestamp_1, timestamp_2, ...]
            }
        All timestamp should have 'YYYY-MM-DD HH:MM:SS:microseconds' format or setting the new values will fail.
        :type app_profile_dict: dict
        """
        if not isinstance(app_profile_dict, dict):
            raise TypeError(expected_type_but_received_message.format("app_profile_dict", "dict", app_profile_dict))

        app_profile_dict_keys = set(app_profile_dict.keys())
        app_profile_attrs = {enum.name for enum in AppProfileAttribute}
        if app_profile_attrs != app_profile_dict_keys:
            raise ValueError(expected_value_but_received_message.format("app_profile_dict_keys", app_profile_attrs,
                                                                        app_profile_dict_keys))

        self.__object_creation_timestamp = datetime.datetime.strptime(
            app_profile_dict[AppProfileAttribute.date_created_timestamp.name], wades_config.datetime_format)
        memory_usages = app_profile_dict[AppProfileAttribute.memory_infos.name]
        cpu_percents = app_profile_dict[AppProfileAttribute.cpu_percents.name]
        child_process_counts = app_profile_dict[AppProfileAttribute.children_counts.name]
        users = app_profile_dict[AppProfileAttribute.usernames.name]
        opened_files = app_profile_dict[AppProfileAttribute.opened_files.name]

        if not (all(isinstance(rss_mem, int) for rss_mem in memory_usages) and
                all(isinstance(cpu_percent, float) for cpu_percent in cpu_percents) and
                all(isinstance(children_count, int) for children_count in child_process_counts) and
                all(isinstance(user, str) for user in users) and
                (isinstance(opened_files, list) and all(
                    isinstance(files, (list, set)) and isinstance(file, str) for files in
                    opened_files for file in files))):
            raise TypeError(expected_type_but_received_message.format("app_profile_dict_values",
                                                                      "Union[dict, str, int, 'float']",
                                                                      app_profile_dict))
        self.__memory_usages = memory_usages

        self.__cpu_percent_usages = cpu_percents
        self.__child_processes_count = child_process_counts
        self.__users = users
        self.__open_files = opened_files

        str_data_retrieval_timestamps = app_profile_dict[AppProfileAttribute.data_retrieval_timestamps.name]
        self.__data_retrieval_timestamp = [datetime.datetime.strptime(retrieval_timestamp, wades_config.datetime_format)
                                           for retrieval_timestamp in str_data_retrieval_timestamps]

    def get_latest_retrieved_data_size(self) -> int:
        """
        Get the latest retrieved data batch size.
        :return: The latest retrieved data batch size.
        :rtype: int
        """
        if len(self.__data_retrieval_timestamp) <= 0:
            return 0
        last_retrieved_data_timestamp = self.__data_retrieval_timestamp[-1]
        return self.__data_retrieval_timestamp.count(last_retrieved_data_timestamp)

    # noinspection DuplicatedCode
    def get_latest_retrieved_data(self) -> dict:
        """
        Get the latest retrieved data as a dictionary. The returned value can be be used for data modelling.
        Note: this method is complementary to `get_previously_retrieved_data`.
        :return: The latest retrieved data in the following format:
            {
                app_name: "Some name",
                data_retrieval_timestamps: [timestamp_1, timestamp_2, ...],
                usernames: [user_1, user_2, ...]
                memory_infos: [2342, 23215, 31573, ...],
                opened_files: [[path_1, path_2, ...], [path_45, ...], ...],
                cpu_percents: [0.2, 13.9, ...],
                children_counts: [1, 5, 0, 4, ...]
            }
        :rtype: dict
        """

        if len(self.__data_retrieval_timestamp) <= 0:
            return dict()

        app_profile_dict = self.dict_format()
        last_retrieved_data_size = self.get_latest_retrieved_data_size()
        app_profile_dict.pop(AppProfileAttribute.date_created_timestamp.name)

        app_profile_dict[AppProfileAttribute.memory_infos.name] = \
            app_profile_dict[AppProfileAttribute.memory_infos.name][-last_retrieved_data_size:]

        app_profile_dict[AppProfileAttribute.cpu_percents.name] = \
            app_profile_dict[AppProfileAttribute.cpu_percents.name][-last_retrieved_data_size:]

        app_profile_dict[AppProfileAttribute.children_counts.name] = \
            app_profile_dict[AppProfileAttribute.children_counts.name][-last_retrieved_data_size:]

        app_profile_dict[AppProfileAttribute.usernames.name] = \
            app_profile_dict[AppProfileAttribute.usernames.name][-last_retrieved_data_size:]

        app_profile_dict[AppProfileAttribute.data_retrieval_timestamps.name] = \
            app_profile_dict[AppProfileAttribute.data_retrieval_timestamps.name][-last_retrieved_data_size:]

        app_profile_dict[AppProfileAttribute.opened_files.name] = \
            app_profile_dict[AppProfileAttribute.opened_files.name][-last_retrieved_data_size:]

        return app_profile_dict

    # noinspection DuplicatedCode
    def get_previously_retrieved_data(self) -> dict:
        """
        Get the previously retrieved data as a dictionary. The returned value can be be used for data modelling.
        Note: this method is complementary to `get_latest_retrieved_data`.
        :return: The previously retrieved data in the following format:
            {
                app_name: "Some name",
                data_retrieval_timestamps: [timestamp_1, timestamp_2, ...],
                usernames: [user_1, user_2, ...]
                memory_infos: [2342, 23215, 31573, ...],
                opened_files: [[path_1, path_2, ...], [path_45, ...], ...],
                cpu_percents: [0.2, 13.9, ...],
                children_counts: [1, 5, 0, 4, ...]
            }
        :rtype: dict
        """
        if len(self.__data_retrieval_timestamp) <= 0:
            return dict()
        app_profile_dict = self.dict_format()

        last_retrieved_data_size = self.get_latest_retrieved_data_size()
        old_data_size = len(self.__data_retrieval_timestamp) - last_retrieved_data_size
        app_profile_dict.pop(AppProfileAttribute.date_created_timestamp.name)

        app_profile_dict[AppProfileAttribute.memory_infos.name] = \
            app_profile_dict[AppProfileAttribute.memory_infos.name][:old_data_size]

        app_profile_dict[AppProfileAttribute.cpu_percents.name] = \
            app_profile_dict[AppProfileAttribute.cpu_percents.name][:old_data_size]

        app_profile_dict[AppProfileAttribute.children_counts.name] = \
            app_profile_dict[AppProfileAttribute.children_counts.name][:old_data_size]

        app_profile_dict[AppProfileAttribute.usernames.name] = \
            app_profile_dict[AppProfileAttribute.usernames.name][:old_data_size]

        app_profile_dict[AppProfileAttribute.data_retrieval_timestamps.name] = \
            app_profile_dict[AppProfileAttribute.data_retrieval_timestamps.name][:old_data_size]

        app_profile_dict[AppProfileAttribute.opened_files.name] = \
            app_profile_dict[AppProfileAttribute.opened_files.name][:old_data_size]

        return app_profile_dict
