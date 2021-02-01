import atexit
import copy
import json
import logging
import threading
import traceback
from socket import socket
from typing import List

from paths import LOGGER_DIR_PATH, LOGGER_TEST_DIR_PATH
from src.main.common.AppProfile import AppProfile
from src.main.common.AppSummary import AppSummary
from src.main.common.Daemon import Daemon
from src.main.common.LoggerUtils import LoggerUtils
from src.main.common.enum.RiskLevel import RiskLevel
from src.main.modeller.FrequencyTechnique import FrequencyTechnique
from src.main.psHandler.AppProfileDataManager import AppProfileDataManager
from wades_config import log_file_extension, modeller_thread_port, localhost_address


class Modeller(Daemon):

    def __init__(self, logger_name: str = "Modeller", is_test: bool = False) -> None:
        """
        Abstracts the daemon that models the collected process information.
        :param logger_name: The name of the logger.
        :type logger_name: str
        :param is_test: Flag for checking if this is called by a test. It changes the log path according to the value.
        :type is_test: bool
        """
        self.__logger_base_dir = LOGGER_DIR_PATH if not is_test else LOGGER_TEST_DIR_PATH
        self.__logger_name = logger_name
        self.__modelled_applications = list()  # Doesn't store non-running applications.
        self.__previous_modelled_retrieval_timestamp = None
        self.__socket = None

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

    @staticmethod
    def __filter_out_non_running_applications(app_profiles: List[AppProfile]) -> List[AppProfile]:
        """
        Filters out applications that are not currently running, as to avoid unnecessary modelling.
        :param app_profiles: The application profiles to filter.
        :type app_profiles: List[AppProfile]
        :return: The applications that are currently running.
        :rtype List[AppProfile]
        """
        running_apps = list()
        latest_retrieval_timestamp = AppProfileDataManager.get_last_retrieved_data_timestamp()
        for app_profile in app_profiles:
            retrieval_timestamps = app_profile.get_data_retrieval_timestamps()
            app_profile_last_retrieved_data_timestamp = retrieval_timestamps[-1]
            if latest_retrieval_timestamp == app_profile_last_retrieved_data_timestamp:
                running_apps.append(app_profile)

        return running_apps

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

        LoggerUtils.setup_logger(self.__logger_name, self.__logger_base_dir / (self.__logger_name + log_file_extension))
        atexit.register(self.__exit_handler, self)
        modelling_thread = threading.Thread(target=self.modelling_thread_run)
        modelling_thread.daemon = True
        modelling_thread.start()
        self.__socket = socket()
        self.__socket.bind((localhost_address, modeller_thread_port))
        self.__socket.listen()
        self.listener_run()

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
                    application_profiles = AppProfileDataManager.get_saved_profiles()
                    running_applications = Modeller.__filter_out_non_running_applications(application_profiles)
                    logger.info("Starting to model {} application profiles.".format(len(running_applications)))
                    self.__modelled_applications = Modeller.model_application_profiles(running_applications)
                    self.__previous_modelled_retrieval_timestamp = actual_last_retrieved_timestamp
                    logger.info("Finished modelling {} application profiles.".format(len(running_applications)))
                    # Save data
                    abnormal_applications = self.get_abnormal_applications()
                    AppProfileDataManager.save_abnormal_apps(abnormal_applications)

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
