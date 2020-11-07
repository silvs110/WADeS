import copy
import datetime
import time

import psutil

from src.utils.error_messages import expected_type_but_received_message
from typing import Union

class Application:

    def __init__(self, process_name: str) -> None:
        """
        Abstracts the Application past and current usages.
        :raises TypeError if process is not of type psutil.Process.
        :param process_name: the information about a process associated to an application.
        :type process_name: str
        """
        if not (isinstance(process_name, str)):
            raise TypeError(expected_type_but_received_message.format("str", "process_name", process_name))

        self.__object_creation_timestamp = datetime.datetime.now()
        self.__name = process_name
        self.__memory_usages = list()  # this is in bytes
        self.__cpu_percent_usages = list()
        self.__open_files = dict()
        self.__data_retrieval_timestamp = list()
        self.__child_processes_count = list()
        self.__users = set()

    def get_application_name(self) -> str:
        """
        Gets the name of the application.
        :return: the name of the application.
        :rtype: str
        """
        return self.__name

    def get_object_creation_timestamp(self) -> datetime.datetime:
        """
        Gets the timestamp this object was created.
        :return: the timestamp this object was created.
        :rtype: datetime.datetime
        """
        return self.__object_creation_timestamp

    def get_memory_usages(self) -> list:
        """
        Gets the memory usages for this application. It will return all recorded memory usages.
        :return: the past memory usages for this application.
        :rtype: list
        """
        return copy.deepcopy(self.__memory_usages)

    def get_open_files(self) -> dict:
        """
        Gets the dictionary of opened files for this application.
        Format:
            {
                file_name: ['r', 'w', 'a', 'a+', 'r+'],
                ...
            }
        :return: a dictionary of opened files and the permissions.
        :rtype: dict
        """
        return copy.deepcopy(self.__open_files)

    def get_data_retrieval_timestamp(self) -> list:
        """
        Gets a list of all the retrieval times.
        :return: list of retrieval times.
        :rtype: list
        """
        return copy.deepcopy(self.__data_retrieval_timestamp)

    def get_child_processes_count(self) -> list:
        """
        Gets a history of all the child processes count.
        :return: a list of all the child processes count.
        :rtype: list
        """
        return copy.deepcopy(self.__child_processes_count)

    def get_users(self) -> set:
        """
        Gets the users that have run this application.
        :return: the set of users that have run this application.
        :rtype: set
        """
        return copy.deepcopy(self.__users)

    def get_cpu_percentages(self) -> list:
        """
        Gets the history of cpu usages for this application.
        :return: the history of the cpu udages for this application.
        :rtype: list
        """
        return copy.deepcopy(self.__cpu_percent_usages)

    def __str__(self) -> str:
        """
        Overload of the method __str__ to display the information about the application in a more readable format.
        :return: the information about the application in a more readable format
        :rtype: str
        """
        return f"Application: {self.__name}"

    def __eq__(self, other: Union["Application", str]) -> bool:
        """
        Overloads the == operator. Two applications are equal if they have the same name.
        :param other: the other application to compare.
        :type other: Union["Application", str]
        :return: True if the two applications have the same name, False otherwise.
        :rtype: bool
        """
        if not isinstance(other, (Application, str)):
            return False
        return self.__name == other or (hasattr(other, "name") and self.__name == other.name)

    def __ne__(self, other: Union["Application", str]) -> bool:
        """
        Overloads the != operator. Two applications are equal if they have the same name.
        :param other: the other application to compare.
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
        :param process: information about the specific process.
        :type process: psutil.Process
        :param data_retrieval_timestamp: the time the data was retrieved.
        :type data_retrieval_timestamp: datetime.datetime
        """
        if not (isinstance(process, psutil.Process)):
            raise TypeError(expected_type_but_received_message.format("psutil.Process", "process", process))
        if not (isinstance(data_retrieval_timestamp, datetime.datetime)):
            raise TypeError(expected_type_but_received_message.format("datetime.datetime", "data_retrieval_timestamp",
                                                                      data_retrieval_timestamp))
        if data_retrieval_timestamp.replace(tzinfo=None) > datetime.datetime.now():
            raise ValueError("Argument data_retrieval_timestamp cannot be newer than current time. Value receive: %s"
                             .format(data_retrieval_timestamp))

        # Get info from the process object. One of the following calls may raise an Error (OS, AccessDenied, etc).
        open_files = process.open_files()
        memory_info = process.memory_info()
        child_process_count = len(process.children())
        username = process.username()
        process.cpu_percent()

        time.sleep(0.1) # wait for cpu_percent to return a meaningful value.
        cpu_percentage = process.cpu_percent()

        self.add_open_files(open_files=open_files)
        self.__memory_usages.append(memory_info.rss)
        self.__data_retrieval_timestamp.append(data_retrieval_timestamp)
        self.__child_processes_count.append(child_process_count)
        self.__users.add(username)
        self.__cpu_percent_usages.append(cpu_percentage)


    def add_new_information(self, memory_usage: int, child_processes_count: int, users: set, open_files: list,
                            cpu_percentage: float, data_retrieval_timestamp: datetime.datetime) -> None:
        """
        Adds new information about this application.
        :raises TypeError if one of the following criteria is met:
            - memory_usage or child_processes_count is not of type 'int'
            - users is not of type 'set'
            - open_files is not of type 'list'
            - cpu_percentage is not of type 'float'
            - data_retrieval_timestamp is not of type 'datetime.datetime'
        :raises ValueError if either memory_usage, child_processes_count or cpu_percentage has negative value.
            Or if data_retrieval_timestamp is newer than current time.
        :param memory_usage: the memory usage of this application.
        :type memory_usage: int
        :param child_processes_count: the number of child process registered at the moment.
        :type child_processes_count: int
        :param users: the users that are running this application.
        :type users: set
        :param open_files: the open files to add.
        :type open_files: list
        :param cpu_percentage: current CPU usage for this application.
        :type cpu_percentage: float
        :param data_retrieval_timestamp: the time the data was retrieved.
        :type data_retrieval_timestamp: datetime.datetime
        """
        if not isinstance(memory_usage, int):
            raise TypeError(expected_type_but_received_message.format("int", "memory_usages", memory_usage))
        if not isinstance(child_processes_count, int):
            raise TypeError(
                expected_type_but_received_message.format("int", "child_processes_count", child_processes_count))
        if not isinstance(users, set):
            raise TypeError(expected_type_but_received_message.format("set", "users", users))
        if not isinstance(open_files, list):
            raise TypeError(expected_type_but_received_message.format("list", "open_files", open_files))
        if not isinstance(cpu_percentage, float):
            raise TypeError(expected_type_but_received_message.format("float", "cpu_percentage", cpu_percentage))
        if not (isinstance(data_retrieval_timestamp, datetime.datetime)):
            raise TypeError(expected_type_but_received_message.format("datetime.datetime", "data_retrieval_timestamp",
                                                                      data_retrieval_timestamp))
        if memory_usage < 0 or child_processes_count < 0 or cpu_percentage < 0:
            raise ValueError(
                "Arguments memory_usage, child_processes_count and cpu_percentage cannot have negative value, "
                "but received [%s, %s, %s]".format(
                    memory_usage, child_processes_count, cpu_percentage))
        if data_retrieval_timestamp.replace(tzinfo=None) > datetime.datetime.now():
            raise ValueError("Argument data_retrieval_timestamp cannot be newer than current time. Value receive: %s"
                             .format(data_retrieval_timestamp))

        self.add_open_files(open_files=open_files)
        self.__memory_usages.append(memory_usage)
        self.__child_processes_count.append(child_processes_count)
        self.__users.update(users)
        self.__cpu_percent_usages.append(cpu_percentage)
        self.__data_retrieval_timestamp.append(data_retrieval_timestamp)

    def add_open_files(self, open_files: list) -> None:
        """
        Adds the open files to the list of open files for this application.
        :raises TypeError if open_files is not of type list.
        :param open_files: the open files to add.
        :type open_files: list
        """
        if not isinstance(open_files, list):
            raise TypeError(expected_type_but_received_message.format("list", "open_files", open_files))

        for open_file in open_files:
            if open_file.path not in self.__open_files:
                self.__open_files[open_file.path] = set()

            if hasattr(open_file, "mode"):
                self.__open_files[open_file.path].add(open_file.mode)
