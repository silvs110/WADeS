import atexit
import json
import logging
import threading
import time
import traceback
from socket import socket

import paths
import wades_config
from src.main.common.Daemon import Daemon
from src.main.common.LoggerUtils import LoggerUtils
from src.main.modeller.Modeller import Modeller
from src.main.psHandler.AppProfileDataManager import AppProfileDataManager
from src.main.psHandler.ProcessHandler import ProcessHandler
from src.utils.error_messages import expected_type_but_received_message


class WadesDaemon(Daemon):
    def __init__(self, logger_name: str = "WadesDaemon") -> None:
        """
        Constructor for Wades Daemon.
        :param logger_name: The name of the logger. Defaults to WadesDaemon.
        :type logger_name: str
        """
        self.__logger_name = logger_name
        self.__logger_base_dir = paths.LOGGER_DIR_PATH if not wades_config.is_test else paths.LOGGER_TEST_DIR_PATH
        LoggerUtils.setup_logger(self.__logger_name, self.__logger_base_dir / (self.__logger_name +
                                                                               wades_config.log_file_extension))
        self.__ps_handler = ProcessHandler(logger_name)
        self.__modeller = Modeller(logger_name)
        self.__socket = None
        self.__run_server = wades_config.run_modeller_server
        self.__stop_modelling = False
        super(WadesDaemon, self).__init__(logger_name)

    def set_modeller_service_flag(self, run_modeller_server_new_value: bool) -> None:
        """
        Set the new value for running the modeller server.
        If True, the server is executed and information can be send to display.
        If False, only the ps_handler and modeller are executed.
        :raises TypeError if run_modeller_server_new_value is not of type 'bool'.
        :param run_modeller_server_new_value: The new value of the flag to run the modeller server.
        :type run_modeller_server_new_value: bool
        """
        if not isinstance(run_modeller_server_new_value, bool):
            raise TypeError(expected_type_but_received_message.format("run_modeller_server_new_value", "bool",
                                                                      run_modeller_server_new_value))
        self.__run_server = run_modeller_server_new_value

    def is_modeller_server_set_up(self) -> bool:
        """
        Checks if the modeller server is running.
        This is only for the part of the modeller responsible for retrieving modelled data.
        :return: True, if the modeller server is running, False, otherwise.
        :rtype: bool
        """
        return self.__run_server

    def run(self) -> None:
        """
        Starts the process handler as a daemon.
        """
        atexit.register(self.__exit_handler, self)
        
        if self.__run_server:
            modelling_thread = threading.Thread(target=self.main_thread_run)
            modelling_thread.daemon = True
            modelling_thread.start()
            self.__socket = socket()
            self.__socket.bind((wades_config.localhost_address, wades_config.modeller_thread_port))
            self.__socket.listen()
            self.service_run()
        else:
            self.main_thread_run()

    def main_thread_run(self) -> None:
        """
        Runs the collecting and modelling server. This should be used as daemonize thread if service is enabled.
        """
        logger = logging.getLogger(self.__logger_name)

        while True:
            # noinspection PyBroadException
            try:
                self.__ps_handler.collect_running_processes_information()
                # Add modeller part here.
                if not self.__stop_modelling:
                    self.__modeller.model_running_applications()

                sleep_time = wades_config.retrieval_periodicity_sec \
                    if wades_config.retrieval_periodicity_sec <= wades_config.max_retrieval_periodicity_sec \
                    else wades_config.max_retrieval_periodicity_sec
                time.sleep(sleep_time)

            except Exception:
                logger.error(traceback.format_exc())

    def service_run(self) -> None:
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
                        data_to_send = self.__modeller.get_modelled_application_as_json()
                        encoded_data = data_to_send.encode()  # Defaults to utf-8
                        connection.sendall(encoded_data)

                    elif data.startswith("abnormal apps"):
                        if data.endswith(" --history"):
                            data_to_send = json.dumps(AppProfileDataManager.get_saved_abnormal_apps())
                        else:
                            data_to_send = self.__modeller.get_modelled_application_as_json()
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
