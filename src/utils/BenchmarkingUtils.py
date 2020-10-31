import time
from typing import Callable

from src.utils.error_messages import expected_type_but_received_message


class BenchmarkingUtils:

    @staticmethod
    def get_method_execution_time_seconds(method_to_execute: Callable) -> float:
        """
        Get the execution time of the a method in seconds.:
        :raises TypeError: error is raised when method_to_execute is not of type 'Callable'
        :param method_to_execute: the method to execute.
        :type method_to_execute: Callable
        :return: the time of the executed method in seconds.
        :rtype: float
        """

        if not isinstance(method_to_execute, Callable):
            actual_method_to_execute_name = getattr(method_to_execute, '__name__', 'Unknown')
            raise TypeError(expected_type_but_received_message.format(actual_method_to_execute_name, 'Callable',
                                                                      type(method_to_execute)))
        start_time = time.time()
        method_to_execute()
        return time.time() - start_time

    @staticmethod
    def print_method_execution_time_seconds(method_to_execute: Callable) -> None:
        """
        Gets the execution time of the provided method and prints it.
        :raises TypeError: error is raised when method_to_execute is not of type 'Callable'
        :param method_to_execute: the method to execute.
        :type method_to_execute: Callable
        """
        method_to_execute_name = getattr(method_to_execute, '__name__', 'Unknown')
        if not isinstance(method_to_execute, Callable):
            raise TypeError(expected_type_but_received_message.format(method_to_execute_name, 'Callable',
                                                                      type(method_to_execute)))
        execution_time = BenchmarkingUtils.get_method_execution_time_seconds(method_to_execute=method_to_execute)
        print(f"It took {execution_time} seconds to execute {method_to_execute_name}")
