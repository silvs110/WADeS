import copy
import datetime
import logging
import time
from typing import Dict, List, Union, Set

import psutil

from src.main.common.AppProfile import AppProfile
from src.main.common.enum.ProcessAttribute import ProcessAttribute
from src.main.psHandler.AppProfileDataManager import AppProfileDataManager
from src.utils.error_messages import expected_type_but_received_message, expected_application_message


class ProcessHandler:

    def __init__(self, logger_name: str = "ProcessHandler"):
        """
        Abstracts the daemon that collects information about the running processes.
        :param logger_name: The name of the logger.
        :type logger_name: str
        """
        self.__detected_app_profile_names = set()
        self.__logger_name = logger_name
        self.__latest_retrieval_time = None
        self.__attrs_to_retrieve = [enum.name for enum in ProcessAttribute if enum.name != 'children_count']

    def get_latest_retrieved_data_timestamp(self) -> Union[None, datetime.datetime]:
        """
        Get the latest retrieved data timestamp.
        :return: The latest retrieved timestamp. Returns None if no data has been retrieved.
        :rtype: Union[None, datetime]
        """
        return self.__latest_retrieval_time

    def get_registered_app_profile_names(self) -> Set[str]:
        """
        Gets the registered AppProfiles as a set.
        :return: The registered AppProfiles as a set.
        :rtype: List[str]
        """
        return copy.deepcopy(self.__detected_app_profile_names)

    def __collect_running_processes_and_group_by_application(self) -> Dict[str, list]:
        """
        Collect the running processes information and group them by application name.
        :return: A map with the application name and its running processes.
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
        logger = logging.getLogger(self.__logger_name)
        for process_dict in process_dicts:

            application_name = process_dict[ProcessAttribute.name.name]
            if application_name not in application_name_to_processes_map:
                application_name_to_processes_map[application_name] = list()
            application_name_to_processes_map[application_name].append(process_dict)

        logger.info(
            "Found processes for applications - {}".format(application_name_to_processes_map.keys())
        )
        return application_name_to_processes_map

    def __get_process_info_as_list_of_dict(self) -> List[dict]:
        """
        Gets the process information as a list of dictionaries.
        :return: A list of dictionaries that contains information about the processes.
        :rtype: List[dict]
        """
        logger = logging.getLogger(self.__logger_name)
        logger.info("Retrieving running processes information.")

        processes_list = list()
        self.__latest_retrieval_time = datetime.datetime.now()
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
                # Default value of "inet IPV4 and IPv6" connections
                connections = process_info[ProcessAttribute.connections.name]
                process_info[ProcessAttribute.connections.name] = len(connections) if connections is not None else 0

            except (psutil.AccessDenied, psutil.NoSuchProcess, psutil.ZombieProcess) as psutil_error:
                logger.exception(psutil_error)

        logger.info("Finished retrieving and handling {} processes.".format(len(processes_list)))

        return processes_list

    def __add_processes_to_application_profile_and_save(self, application_name: str,
                                                        application_processes: List[dict]) -> None:
        """
        Adds the process information to its respective application profile.
        :raises TypeError if application_name is not of type 'str' or application_processes is not pf type 'List[dict]'.
        :raises ValueError if at least one of the processes' names is not equal to the application_name provided.
        :param application_name: The name of the application.
        :type application_name: str
        :param application_processes: The list of processes associated to the application.
        :type application_processes: List[dict]
        """
        if not isinstance(application_name, str):
            raise TypeError(expected_type_but_received_message.format("application_name", 'str', application_name))
        if not isinstance(application_processes, list):
            raise TypeError(expected_type_but_received_message.format("application_processes", 'List[dict]',
                                                                      application_processes))
        saved_app_profile = AppProfileDataManager.get_saved_profile(application_name)
        if saved_app_profile is None:
            saved_app_profile = AppProfile(application_name=application_name)

        for process in application_processes:
            if not isinstance(process, dict):
                raise TypeError(expected_type_but_received_message.format("application_processes", 'List[dict]',
                                                                          application_processes))
            process_name = process[ProcessAttribute.name.name]
            if process_name != application_name:
                raise ValueError(expected_application_message.format(application_name, process_name))

            rss_memory = process[ProcessAttribute.memory_info.name].rss
            children_count = process[ProcessAttribute.children_count.name]
            users = [process[ProcessAttribute.username.name]] if process[ProcessAttribute.username.name] is not None \
                else list()
            open_files = process.get(ProcessAttribute.open_files.name, list())
            open_files = open_files if open_files is not None else list()
            cpu_percentage = process[ProcessAttribute.cpu_percent.name]
            num_threads = process[ProcessAttribute.num_threads.name]
            connections_num = process[ProcessAttribute.connections.name]
            saved_app_profile.add_new_information(memory_usage=rss_memory, child_processes_count=children_count,
                                                  users=users,
                                                  open_files=open_files, cpu_percentage=cpu_percentage,
                                                  data_retrieval_timestamp=self.__latest_retrieval_time,
                                                  threads_number=num_threads, connections_num=connections_num)
        AppProfileDataManager.save_app_profile(saved_app_profile)

    def collect_running_processes_information(self) -> None:
        """
        Collects running process information. To get the information call get_registered_app_profiles_as_dict.
        """
        logger = logging.getLogger(self.__logger_name)
        logger.info("Started retrieving running processes information.")
        app_name_to_processes_map = self.__collect_running_processes_and_group_by_application()
        self.__detected_app_profile_names = set(app_name_to_processes_map.keys())
        for app_name, processes in app_name_to_processes_map.items():
            self.__add_processes_to_application_profile_and_save(application_name=app_name,
                                                                 application_processes=processes)
        AppProfileDataManager.save_last_retrieved_data_timestamp(self.__latest_retrieval_time)

    @staticmethod
    def is_application_recently_retrieved(app_profile: AppProfile) -> bool:
        """
        Checks if the application profile provided was recently retrieved.
        :param app_profile: The application profile to check.
        :type app_profile: AppProfile
        :return: True if the application profile was recently retrieved, False otherwise.
        :rtype: bool
        """
        latest_retrieval_timestamp = AppProfileDataManager.get_last_retrieved_data_timestamp()
        retrieval_timestamps = app_profile.get_data_retrieval_timestamps()
        app_profile_last_retrieved_data_timestamp = retrieval_timestamps[-1]
        return latest_retrieval_timestamp == app_profile_last_retrieved_data_timestamp
