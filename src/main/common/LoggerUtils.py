import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

from src.utils.error_messages import expected_type_but_received_message
from wades_config import logging_level, log_file_max_size_bytes, max_number_rotating_log_files


class LoggerUtils:

    @staticmethod
    def setup_logger(logger_name: str, log_file: Path) -> None:
        """
        Sets up a logger with the provided name and log output. The level is set in 'wades_config.py'
        :raises TypeError if logger_name is not of type 'str', or if log_file i not of type 'pathlib.Path'.
        :param logger_name: The name of the new logger. It should be the class name.
        :type logger_name: str
        :param log_file: The file where the logs should be outputted.
        :type log_file: pathlib.Path
        """

        if not isinstance(logger_name, str):
            raise TypeError(expected_type_but_received_message.format("logger_name", "str", logger_name))
        if not isinstance(log_file, Path):
            raise TypeError(expected_type_but_received_message.format("log_file", "pathlib.Path", log_file))

        if not log_file.parent.exists():
            log_file.mkdir(parents=True, exist_ok=True)
        logger = logging.getLogger(logger_name)
        formatter = logging.Formatter('%(asctime)s : %(message)s')
        file_handler = RotatingFileHandler(filename=log_file,
                                           mode='a+',
                                           maxBytes=log_file_max_size_bytes,
                                           backupCount=max_number_rotating_log_files
                                           )

        file_handler.setFormatter(formatter)
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(formatter)

        logger.setLevel(logging_level)
        logger.addHandler(file_handler)
        logger.addHandler(stream_handler)
