import atexit
import copy
import datetime
import logging
import time
import traceback
from pprint import pprint
from typing import Dict, List, Set, Union

import psutil

from paths import LOGGER_DIR_PATH, LOGGER_TEST_DIR_PATH
from src.main.common.AppProfile import AppProfile
from src.main.common.Daemon import Daemon
from src.main.common.LoggerUtils import LoggerUtils
from src.main.common.enum.ProcessAttribute import ProcessAttribute
from src.main.psHandler.AppProfileDataManager import AppProfileDataManager
from src.utils.error_messages import expected_type_but_received_message, expected_application_message
from wades_config import retrieval_periodicity_sec, max_retrieval_periodicity_sec, log_file_extension


class ProcessHandler(Daemon):

    def __init__(self, logger_name: str = "ProcessHandler", is_test: bool = False):
        """
        Abstracts the daemon that collects information about the running processes.
        :param logger_name: The name of the logger.
        :type logger_name: str
        :param is_test: Flag for checking if this is called by a test. It changes the log path according to the value.
        :type is_test: bool
        """
        self.__logger_base_dir = LOGGER_DIR_PATH if not is_test else LOGGER_TEST_DIR_PATH
        self.__logger_name = logger_name
        self.__registered_app_profiles = dict()
        self.__latest_retrieval_time = None
        self.__attrs_to_retrieve = [enum.name for enum in ProcessAttribute if enum.name != 'children_count']

        super(ProcessHandler, self).__init__(logger_name)

    def get_latest_retrieved_data_timestamp(self) -> Union[None, datetime.datetime]:
        """
        Get the latest retrieved data timestamp.
        :return: The latest retrieved timestamp. Returns None if no data has been retrieved.
        :rtype: Union[None, datetime]
        """
        return self.__latest_retrieval_time

    def get_registered_app_profiles_as_dict(self) -> Dict[str, AppProfile]:
        """
        Gets the registered AppProfiles as a dictionary.
        Format:
            {
                application_name: app_profile_1,
                application_name_2: app_profile_2,
                ...
            }
        :return: The registered AppProfiles as a dictionary.
        :rtype: Dict[str, AppProfile]
        """
        return copy.deepcopy(self.__registered_app_profiles)

    def get_registered_app_profiles_list(self) -> List[AppProfile]:
        """
        Gets the registered AppProfiles as a list.
        :return: The registered AppProfiles as a list.
        :rtype: List[AppProfile]
        """
        return list(self.__registered_app_profiles.values())

    def get_registered_application_names(self) -> Set[str]:
        """
        Gets the name of the registered applications.
        :return: The name of the registered applications.
        :rtype: Set[str]
        """
        return set(self.__registered_app_profiles.keys())

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

    def __add_processes_to_application_profile(self, application_name: str, application_processes: List[dict]) -> None:
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
            users = [process[ProcessAttribute.username.name]] if process[ProcessAttribute.username.name] is not None \
                else list()
            open_files = process.get(ProcessAttribute.open_files.name, list())
            open_files = open_files if open_files is not None else list()
            cpu_percentage = process[ProcessAttribute.cpu_percent.name]
            num_threads = process[ProcessAttribute.num_threads.name]
            connections_num = process[ProcessAttribute.connections.name]
            app_profile.add_new_information(memory_usage=rss_memory, child_processes_count=children_count, users=users,
                                            open_files=open_files, cpu_percentage=cpu_percentage,
                                            data_retrieval_timestamp=self.__latest_retrieval_time,
                                            threads_number=num_threads, connections_num=connections_num)

    def collect_running_processes_information(self) -> None:
        """
        Collects running process information. To get the information call get_registered_app_profiles_as_dict.
        """
        logger = logging.getLogger(self.__logger_name)
        logger.info("Started retrieving running processes information.")
        app_name_to_processes_map = self.__collect_running_processes_and_group_by_application()
        for app_name, processes in app_name_to_processes_map.items():
            self.__add_processes_to_application_profile(application_name=app_name,
                                                        application_processes=processes)
        logger.info("Finished retrieving running processes information.")

    def __exit_handler(self) -> None:
        """
        This is called when the Daemon exits.
        """
        AppProfileDataManager.save_app_profiles(self.get_registered_app_profiles_list(),
                                                retrieval_timestamp=self.__latest_retrieval_time)

    def run(self) -> None:
        """
        Starts the process handler as a daemon.
        """
        atexit.register(self.__exit_handler, self)
        LoggerUtils.setup_logger(self.__logger_name, self.__logger_base_dir / (self.__logger_name + log_file_extension))
        logger = logging.getLogger(self.__logger_name)
        while True:
            # noinspection PyBroadException
            try:
                saved_app_profiles = AppProfileDataManager.get_saved_profiles()
                self.__registered_app_profiles = \
                    {app_profile.get_application_name(): app_profile for app_profile in saved_app_profiles}

                self.collect_running_processes_information()
                AppProfileDataManager.save_app_profiles(app_profiles=self.get_registered_app_profiles_list(),
                                                        retrieval_timestamp=self.__latest_retrieval_time)
                sleep_time = retrieval_periodicity_sec \
                    if retrieval_periodicity_sec <= max_retrieval_periodicity_sec else max_retrieval_periodicity_sec
                time.sleep(sleep_time)
            except Exception:
                logger.error(traceback.format_exc())

