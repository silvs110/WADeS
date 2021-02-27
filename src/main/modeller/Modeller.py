import atexit
import copy
import json
import logging
import threading
import traceback
from socket import socket
from time import sleep
from typing import List

import paths
import wades_config
from src.main.common.AppProfile import AppProfile
from src.main.common.AppSummary import AppSummary
from src.main.common.Daemon import Daemon
from src.main.common.LoggerUtils import LoggerUtils
from src.main.common.enum.RiskLevel import RiskLevel
from src.main.modeller.FrequencyTechnique import FrequencyTechnique
from src.main.psHandler.AppProfileDataManager import AppProfileDataManager
from src.utils.error_messages import expected_type_but_received_message


class Modeller(Daemon):

    def __init__(self, logger_name: str = "Modeller") -> None:
        """
        Abstracts the daemon that models the collected process information.
        :param logger_name: The name of the logger.
        :type logger_name: str
        """
        self.__logger_base_dir = paths.LOGGER_DIR_PATH if not wades_config.is_test else paths.LOGGER_TEST_DIR_PATH
        self.__logger_name = logger_name
        self.__modelled_applications = list()  # Doesn't store non-running applications.
        self.__previous_modelled_retrieval_timestamp = None
        self.__socket = None
        self.__run_server = wades_config.run_modeller_server
        self.__stop_modelling = False
        super(Modeller, self).__init__(logger_name)

    @staticmethod
    def model_application_profiles(application_profiles: List[AppProfile]) -> List[AppSummary]:
        """
        Create the frequency model for a list of AppProfiles. This is the main method of this class.
        :param application_profiles: the application profiles to model.
        :type application_profiles: List[AppProfile]
        :return: the model of the provided application profiles.
        :rtype List[AppSummary]
        """
        frequency_technique = FrequencyTechnique()

        return frequency_technique(application_profiles)

    def get_modelled_applications(self) -> List[AppSummary]:
        """
        Gets the modelled applications.
        :return: The modelled applications.
        :rtype: List[AppSummary]
        """
        return copy.deepcopy(self.__modelled_applications)

    def is_modeller_server_set_up(self) -> bool:
        """
        Checks if the modeller server is running.
        This is only for the part of the modeller responsible for retrieving modelled data.
        :return: True, if the modeller server is running, False, otherwise.
        :rtype: bool
        """
        return self.__run_server

    def get_abnormal_applications(self) -> List[AppSummary]:
        """
        Gets the list of abnormal applications.
        :return: The abnormal applications.
        :rtype: List[AppSummary]
        """
        abnormal_applications = list()
        for app_summary in self.__modelled_applications:

            app_risk_level = app_summary.get_risk_level()
            if app_risk_level is not RiskLevel.none:
                abnormal_applications.append(app_summary)
        return abnormal_applications

    def set_modeller_service_flag(self, run_modeller_server_new_value: bool) -> None:
        """
        Set the new value for running the modeller server.
        If True, the server is executed and information can be send to display.
        If False, only the modelling of the application is executed.
        :raises TypeError if run_modeller_server_new_value is not of type 'bool'.
        :param run_modeller_server_new_value: The new value of the flag to run the modeller server.
        :type run_modeller_server_new_value: bool
        """
        if not isinstance(run_modeller_server_new_value, bool):
            raise TypeError(expected_type_but_received_message.format("run_modeller_server_new_value", "bool",
                                                                      run_modeller_server_new_value))
        self.__run_server = run_modeller_server_new_value

    @staticmethod
    def __is_application_recently_retrieved(app_profile: AppProfile) -> bool:
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

    @staticmethod
    def __convert_modelled_apps_to_json(modelled_apps: List[AppSummary]) -> str:
        """
        Converts a list of modelled apps into a json object.
        It should be used for preparing data to send to connected clients.
        :param modelled_apps: The modelled applications.
        :type modelled_apps: List[AppSummary]
        :return: The modelled apps as a json object.
        :rtype: str
        """
        modelled_apps_dict = [str(modelled_app) for modelled_app in modelled_apps]
        return json.dumps(modelled_apps_dict)

    def run(self) -> None:
        """
        Starts the modeller as a daemon. This method overrides the method in the parent class.
        """

        LoggerUtils.setup_logger(self.__logger_name, self.__logger_base_dir / (self.__logger_name +
                                                                               wades_config.log_file_extension))
        atexit.register(self.__exit_handler, self)
        if self.__run_server:
            modelling_thread = threading.Thread(target=self.modelling_thread_run)
            modelling_thread.daemon = True
            modelling_thread.start()
            self.__socket = socket()
            self.__socket.bind((wades_config.localhost_address, wades_config.modeller_thread_port))
            self.__socket.listen()
            self.listener_run()
        else:
            self.modelling_thread_run()

    def modelling_thread_run(self) -> None:
        """
        Runs the modelling algorithm. This should be used as daemonize thread.
        """
        logger = logging.getLogger(self.__logger_name)
        while True:
            actual_last_retrieved_timestamp = AppProfileDataManager.get_last_retrieved_data_timestamp()
            # noinspection PyBroadException
            try:
                if not self.__stop_modelling and (self.__previous_modelled_retrieval_timestamp is None
                                                  or (actual_last_retrieved_timestamp is not None
                                                      and self.__previous_modelled_retrieval_timestamp is not None
                                                      and actual_last_retrieved_timestamp >
                                                      self.__previous_modelled_retrieval_timestamp)):
                    saved_application_profile_names = AppProfileDataManager.get_saved_app_profiles_names()
                    modelled_apps = list()
                    for saved_app_profile_name in saved_application_profile_names:
                        app_profile = AppProfileDataManager.get_saved_profile(saved_app_profile_name)
                        if Modeller.__is_application_recently_retrieved(app_profile):
                            modelled_app = Modeller.model_application_profiles([app_profile])
                            modelled_apps.extend(modelled_app)

                    self.__previous_modelled_retrieval_timestamp = actual_last_retrieved_timestamp
                    self.__modelled_applications = modelled_apps
                    logger.info("Finished modelling {} application profiles.".format(len(modelled_apps)))
                    # Save data
                    abnormal_applications = self.get_abnormal_applications()
                    AppProfileDataManager.save_abnormal_apps(abnormal_applications)
                else:
                    sleep(wades_config.retrieval_periodicity_sec)

            except Exception:
                logger.error(traceback.format_exc())

    def listener_run(self) -> None:
        """
        Runs the listener service thread. All request send by the ui/front-end will be handled here.
        """
        logger = logging.getLogger(self.__logger_name)
        while True:
            # noinspection PyBroadException
            try:
                connection, address = self.__socket.accept()
                with connection:

                    data_raw = connection.recv(1024)
                    data = data_raw.decode()
                    logger.info("Request received {} from {}".format(data, address))
                    if data == "modelled apps":
                        data_to_send = Modeller.__convert_modelled_apps_to_json(
                            modelled_apps=self.__modelled_applications)
                        encoded_data = data_to_send.encode()  # Defaults to utf-8
                        connection.sendall(encoded_data)

                    elif data.startswith("abnormal apps"):
                        if data.endswith(" --history"):
                            data_to_send = json.dumps(AppProfileDataManager.get_saved_abnormal_apps())
                        else:
                            data_to_send = Modeller.__convert_modelled_apps_to_json(
                                modelled_apps=self.get_abnormal_applications())
                        encoded_data = data_to_send.encode()  # Defaults to utf-8
                        connection.sendall(encoded_data)

                    elif data == "modeller pause":
                        self.__stop_modelling = True
                        logger.info("Starting modelling")

                    elif data == "modeller continue":
                        self.__stop_modelling = False
                        logger.info("Stopping modelling")

                    elif data == "modeller status":
                        data_raw = ["Modelling paused."] if self.__stop_modelling else ["Modelling running."]
                        data_to_send = json.dumps(data_raw)
                        connection.sendall(data_to_send.encode())
                    else:
                        data_to_send = json.dumps(["Command not supported"])
                        connection.sendall(data_to_send.encode())

            except Exception:
                logger.error(traceback.format_exc())

    def __exit_handler(self) -> None:
        """
        Used to clean up the daemon's socket.
        """
        if isinstance(self.__socket, socket):
            self.__socket.close()
