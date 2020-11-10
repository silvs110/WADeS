import copy
import datetime
import logging
import time
from typing import Dict, List, Set

import psutil

from src.main.AppProfile import AppProfile
from src.main.ProcessAttribute import ProcessAttribute
from src.utils.error_messages import expected_type_but_received_message, expected_application_message


class ProcessHandler:

    def __init__(self):
        """
        Abstracts the object that handles processes running in the system.
        """
        self.__registered_app_profiles = dict()
        self.__previous_retrieval_time = None
        self.__attrs_to_retrieve = [enum.name for enum in ProcessAttribute if enum.name != 'children_count']

    def get_registered_app_profiles_as_dict(self) -> Dict[str, AppProfile]:
        """
        Gets the registered AppProfiles as a dictionary.
        Format:
            {
                application_name: app_profile_1,
                application_name_2: app_profile_2,
                ...
            }
        :return: the registered AppProfiles as a dictionary.
        :rtype: Dict[str, AppProfile]
        """
        return copy.deepcopy(self.__registered_app_profiles)

    def get_registered_app_profiles_list(self) -> List[AppProfile]:
        """
        Gets the registered AppProfiles as a list.
        :return: the registered AppProfiles as a list.
        :rtype: List[AppProfile]
        """
        return list(self.__registered_app_profiles.values())

    def get_registered_application_names(self) -> Set[str]:
        """
        Gets the name of the registered applications.
        :return: the name of the registered applications.
        :rtype: Set[str]
        """
        return set(self.__registered_app_profiles.keys())

    def __collect_running_processes_and_group_by_application(self) -> Dict[str, list]:
        """
        Collect the running processes information and group them by application name.
        :return: a map with the application name and its running processes.
            Format:
                {
                    application_name_1: [process_dict_1, process_dict_2],
                    application_name_2: [...],
                    ...
                }
        :rtype: Dict[str, Dict[int, psutil.Process]]
        """
        application_name_to_processes_map = dict()
        process_dicts = self.__get_process_info_as_list_of_dict()
        for process_dict in process_dicts:
            application_name = process_dict[ProcessAttribute.name.name]
            if application_name not in application_name_to_processes_map:
                application_name_to_processes_map[application_name] = list()
            application_name_to_processes_map[application_name].append(process_dict)
        return application_name_to_processes_map

    def __get_process_info_as_list_of_dict(self) -> List[dict]:
        """
        Gets the process information as a list of dictionaries.
        :return: a list of dictionaries that contains information about the processes.
        :rtype: List[dict]
        """
        processes_list = list()
        self.__previous_retrieval_time = datetime.datetime.now()
        processes = list(psutil.process_iter())
        for process in processes:
            try:
                process.cpu_percent()
            except (psutil.AccessDenied, psutil.NoSuchProcess, psutil.ZombieProcess):
                continue
        time.sleep(0.1)  # Wait for cpu_percent value returns meaningful value. More info:
        # https://psutil.readthedocs.io/en/latest/#psutil.Process.cpu_percent

        for process in processes:
            try:
                process_info = process.as_dict(attrs=self.__attrs_to_retrieve)
                process_info[ProcessAttribute.children_count.name] = len(process.children())
                processes_list.append(process_info)

            except (psutil.AccessDenied, psutil.NoSuchProcess, psutil.ZombieProcess) as psutil_error:
                logging.exception(psutil_error)
        return processes_list

    def __add_processes_to_application_profile(self, application_name: str, application_processes: List[dict]) -> None:
        """
        Adds the process information to its respective application profile.
        :raises TypeError if application_name is not of type 'str' or application_processes is not pf type 'List[dict]'.
        :raises ValueError if at least one of the processes' names is not equal to the application_name provided.
        :param application_name: the name of the application.
        :type application_name: str
        :param application_processes: the list of processes associated to the application.
        :type application_processes: List[dict]
        """
        if not isinstance(application_name, str):
            raise TypeError(expected_type_but_received_message.format("application_name", 'str', application_name))
        if not isinstance(application_processes, list):
            raise TypeError(expected_type_but_received_message.format("application_processes", 'List[dict]',
                                                                      application_processes))
        for process in application_processes:
            if not isinstance(process, dict):
                raise TypeError(expected_type_but_received_message.format("application_processes", 'List[dict]',
                                                                          application_processes))
            process_name = process[ProcessAttribute.name.name]
            if process_name != application_name:
                raise ValueError(expected_application_message.format(application_name, process_name))

            if process_name not in self.__registered_app_profiles.keys():
                self.__registered_app_profiles[process_name] = AppProfile(application_name=process_name)

            app_profile = self.__registered_app_profiles[process_name]
            rss_memory = process[ProcessAttribute.memory_info.name].rss
            children_count = process[ProcessAttribute.children_count.name]
            users = {process[ProcessAttribute.username.name]}
            open_files = process.get(ProcessAttribute.open_files.name, list())
            open_files = open_files if open_files is not None else list()
            cpu_percentage = process[ProcessAttribute.cpu_percent.name]
            app_profile.add_new_information(memory_usage=rss_memory, child_processes_count=children_count, users=users,
                                            open_files=open_files, cpu_percentage=cpu_percentage,
                                            data_retrieval_timestamp=self.__previous_retrieval_time)

    def collect_running_processes_information(self) -> None:
        """
        Collects running process information. To get the information call get_registered_app_profiles_as_dict.
        """
        app_name_to_processes_map = self.__collect_running_processes_and_group_by_application()
        for app_name, processes in app_name_to_processes_map.items():
            self.__add_processes_to_application_profile(application_name=app_name,
                                                        application_processes=processes)
