import copy
import datetime
import logging
import time
from typing import Dict, List, Set

import psutil

from src.main.Application import Application
from src.utils.error_messages import expected_type_but_received_message, expected_application_message


class ProcessHandler:

    def __init__(self):
        """
        Abstracts the object that handles processes running in the system.
        """
        self.__registered_applications = dict()
        self.__previous_retrieval_time = None

    def get_registered_applications_as_dict(self) -> Dict[str, Application]:
        """
        Gets the registered applications as a dictionary.
        Format:
            {
                application_name: application_object,
                application_name_2: application_object_2,
                ...
            }
        :return: the registered applications as a dictionary.
        :rtype: Dict[str, Application]
        """
        return copy.deepcopy(self.__registered_applications)

    def get_registered_applications_list(self) -> List[Application]:
        """
        Gets the registered applications as a list.
        :return: the registered applications as a list.
        :rtype: List[Application]
        """
        return list(self.__registered_applications.values())

    def get_registered_application_names(self) -> Set[str]:
        """
        Gets the name of the registered applications.
        :return: the name of the registered applications.
        :rtype: Set[str]
        """
        return set(self.__registered_applications.keys())

    def collect_running_process_and_group_by_application(self) -> Dict[str, Dict[int, psutil.Process]]:
        """
        Collect the running processes information and group them by application name.
        :return: a map with the application name and its running processes.
            Format:
                {
                    application_name_1: {
                        pid_1: process_object_1,
                        pid_2: process_object_2,
                        ...
                    }, application_name_2: {
                        ...
                    },
                    ...
                }
        :rtype: Dict[str, Dict[int, psutil.Process]]
        """
        application_name_to_processes_map = dict()
        self.__previous_retrieval_time = datetime.datetime.now()
        processes = psutil.process_iter()
        for process in processes:
            process_name = process.name()
            if process_name not in application_name_to_processes_map:
                application_name_to_processes_map[process_name] = dict()
            application_name_to_processes_map[process_name][process.pid] = process
        return application_name_to_processes_map

    def add_application_processes_to_application_profile(self, applications_dict: Dict[str, Dict[int, psutil.Process]]) -> None:
        """
        Add application process object to application profile.
        :raises TypeError if applications_dict is not of type 'Dict[str, Dict[int, psutil.Process]]'.
        :param applications_dict: a dictionary with application the name of the application and running processes
        associated with that application.
            Format:
                {
                    application_name_1: {
                        pid_1: process_object_1,
                        pid_2: process_object_2,
                        ...
                    }, application_name_2: {
                        ...
                    },
                    ...
                }
        :type applications_dict: Dict[str, Dict[int, psutil.Process]]
        """
        if not isinstance(applications_dict, dict):
            raise TypeError(expected_type_but_received_message.format("applications_dict", "Dict[int, psutil.Process]]",
                                                                      applications_dict))
        for application_name, processes in applications_dict.items():
            if not isinstance(processes, dict):
                raise TypeError(expected_type_but_received_message.format("applications_dict", "Dict[int, "
                                                                                               "psutil.Process]]",
                                                                          applications_dict))
            processes_objects = processes.values()
            for process in processes_objects:
                self.add_process_to_application_profile(process=process)

    def add_application_processes_info_to_application_profile(self, applications_dict: Dict[str, Dict[int, psutil.Process]]) -> None:
        """
        Add application process information to application profile.
        :raises TypeError if applications_dict is not of type 'Dict[str, Dict[int, psutil.Process]]'.
        :param applications_dict: a dictionary with application the name of the application and running processes
        associated with that application.
            Format:
                {
                    application_name_1: {
                        pid_1: process_object_1,
                        pid_2: process_object_2,
                        ...
                    }, application_name_2: {
                        ...
                    },
                    ...
                }
        :type applications_dict: Dict[str, Dict[int, psutil.Process]]
        """
        if not isinstance(applications_dict, dict):
            raise TypeError(expected_type_but_received_message.format("applications_dict", "Dict[int, psutil.Process]]",
                                                                      applications_dict))
        for application_name, processes in applications_dict.items():
            if not isinstance(processes, dict):
                raise TypeError(expected_type_but_received_message.format("applications_dict", "Dict[int, "
                                                                                               "psutil.Process]]",
                                                                          applications_dict))

            if application_name not in self.__registered_applications.keys():
                self.__registered_applications[application_name] = Application(process_name=application_name)
            application = self.__registered_applications[application_name]

            processes_objects = processes.values()
            valid_processes = list()
            for process in processes_objects:
                try:
                    process.cpu_percent()
                except (psutil.AccessDenied, psutil.ZombieProcess, psutil.NoSuchProcess) as psutil_error:
                    logging.error(psutil_error)
                    continue
                valid_processes.append(process)
            time.sleep(0.1)  # Wait for cpu_percent to update
            # For more info: https://stackoverflow.com/questions/39119119/psutil-get-cpu-of-all-processes
            for process in valid_processes:
                try:
                    open_files = process.open_files()
                    rss_memory_info = process.memory_info().rss
                    child_process_count = len(process.children())
                    cpu_percentage = process.cpu_percent()
                    username = process.username()
                except (psutil.AccessDenied, psutil.ZombieProcess, psutil.NoSuchProcess) as psutil_error:
                    logging.error(psutil_error)
                    continue
                application.add_new_information(memory_usage=rss_memory_info, child_processes_count=child_process_count,
                                                users={username}, open_files=open_files, cpu_percentage=cpu_percentage,
                                                data_retrieval_timestamp=self.__previous_retrieval_time)

    def add_process_to_application_profile(self, process: psutil.Process) -> None:
        """
        Add process information using process object to Application Profile.
        :raises TypeError if process is not of type 'psutil.Process'.
        :param process: the process to add.
        :type process: psutil.Process
        """
        if not isinstance(process, psutil.Process):
            raise TypeError(expected_type_but_received_message.format("process", "psutil.Process", process))

        application_name = process.name()
        if application_name not in self.__registered_applications.keys():
            self.__registered_applications[application_name] = Application(process_name=application_name)
        application = self.__registered_applications[application_name]

        try:
            application.add_new_information_from_process_object(process=process,
                                                                data_retrieval_timestamp=self.__previous_retrieval_time)
        except (psutil.AccessDenied, psutil.NoSuchProcess) as psutil_error:
            logging.info(str(psutil_error))

    @staticmethod
    def collect_application_processes_properties(processes: List[psutil.Process]) -> dict:
        """
        Collects an application processes information and convert the data into dictionary.
        The following processes information is collected:
            - open files
            - rss
            - users
            - cpu_percentage
        :raises TypeError if processes is not of type 'List[psutil.Process]'.
        :raises ValueError if a process that belongs to another application is found.
        :param processes: the list of processes.
        :type processes: List[psutil.Process]
        :return: a dictionary with the collected information.
            Format:
                {
                    open_files: [popenfile(path='some/path', fd=3, position=0, mode='w', flags=32769), ...],
                    rss: 453434 (in bytes),
                    cpu_usage: 78.3,
                    users: {some_user, other_user, ...}
                }
        :rtype: dict
        """
        if not isinstance(processes, list):
            raise TypeError(expected_type_but_received_message.format("processes", "List[psutil.Process]", processes))

        application_name = None
        all_open_files = list()
        rss_used_by_all_processes = 0
        total_cpu_percentage_usage = 0
        all_users = set()
        existing_processes = list()
        for process in processes:
            if not isinstance(process, psutil.Process):
                raise TypeError(
                    expected_type_but_received_message.format("processes", "List[psutil.Process]", processes))
            try:
                process_name = process.name()
                if application_name is None:
                    application_name = process_name
                elif application_name != process_name:
                    raise ValueError(expected_application_message.format(application_name, process_name))
                process.cpu_percent()
            except psutil.NoSuchProcess:
                logging.error("PID: {} not found".format(process.pid))
                continue
            existing_processes.append(process)

        time.sleep(.1)  # Update cpu_percent values

        for process in existing_processes:
            try:
                open_files = process.open_files()
                memory_info = process.memory_info()
                rss_info = memory_info.rss
                cpu_percentage = process.cpu_percent()
                username = process.username()
                all_open_files.extend(open_files)
                rss_used_by_all_processes += rss_info
                total_cpu_percentage_usage += cpu_percentage
                all_users.add(username)
            except (psutil.AccessDenied, psutil.NoSuchProcess) as psutil_exception:
                logging.info(str(psutil_exception))

        return {
            "open_files": all_open_files,
            "rss": rss_used_by_all_processes,
            "cpu_usage": total_cpu_percentage_usage,
            "users": all_users
        }

    @staticmethod
    def find_ppids_from_application_processes(processes: List[psutil.Process]) -> set:
        """
        Find parent(s) process ID.
        :raises TypeError if processes is not of type 'List[psutil.Process]'.
        :param processes: the processes to check.
        :type processes: List[psutil.Process]
        :return: a collection of the PPIDs.
        :rtype: set
        """
        if not isinstance(processes, list):
            raise TypeError(expected_type_but_received_message.format("processes", "list", processes))
        # Looks at all the children PIDS and PIDS, and compare the two sets.
        all_children_pid = set()
        process_pids = set()
        if len(processes) == 1:
            return {processes[0].pid}
        for process in processes:
            if not isinstance(process, psutil.Process):
                raise TypeError(
                    expected_type_but_received_message.format("processes", "List[psutil.Process]", processes))
            try:
                process_pids.add(process.pid)
                child_processes = process.children()
                all_children_pid.update({child_process.pid for child_process in child_processes})
            except (psutil.AccessDenied, psutil.NoSuchProcess) as psutil_exception:
                logging.info(str(psutil_exception))
        return process_pids.difference(all_children_pid)
