import logging
from typing import Union

import psutil
from daemon import DaemonContext, pidfile

from paths import WADES_DIR_PATH
from src.utils.error_messages import method_not_implemented_error_message
from wades_config import pid_file_extension


class Daemon:
    def __init__(self, logger: logging.Logger, daemon_name: str) -> None:
        """
        Initializes the class using a logger and daemon name.
        :param logger: The logger used to record the required information.
        :type logger: logging
        :param daemon_name: The name of the daemon.
        :type daemon_name: str
        """
        file_name = daemon_name if daemon_name.endswith(pid_file_extension) else daemon_name + pid_file_extension
        self.__file_path = WADES_DIR_PATH / file_name
        self.__logger = logger
        self.__daemon_name = daemon_name

    def run(self) -> None:
        """
        Abstract method.
        """
        raise NotImplementedError(method_not_implemented_error_message.format("src.main.common.Daemon.Daemon.run"))

    def terminate(self) -> None:
        """
        Terminates the running daemon.
        """
        pid = self.__get_pid()
        try:
            daemon_process = psutil.Process(pid)
            daemon_process.terminate()
        except psutil.NoSuchProcess:
            self.__logger.info("Daemon with pid {} could not killed as it was not found.".format(pid))

    def __get_pid(self) -> Union[int, None]:
        """
        Retrieves the PID from the PID file.
        :return: the PID of the daemon, None otherwise.
        :rtype: Union[int, None]
        """
        try:
            with open(self.__file_path, 'r') as file:

                pid = int(file.read().strip())
                return pid

        except (ValueError, FileNotFoundError, IOError):
            return None

    def start(self) -> None:
        """
        Starts the daemon.
        """
        if not self.__get_pid():
            self.__logger.info("Starting Daemon {}".format(self.__daemon_name))
            paths_to_preserve = [handler.baseFilename for handler in self.__logger.handlers
                                 if isinstance(handler, logging.FileHandler)]

            with DaemonContext(pidfile=pidfile.PIDLockFile(self.__file_path),
                               working_directory=WADES_DIR_PATH,
                               files_preserve=paths_to_preserve):
                self.run()
