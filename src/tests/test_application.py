import datetime

import psutil
import pytest
from psutil import AccessDenied

from src.main.Application import Application

"""
This file contains test for Application class.
Functional test for the following methods in Application class:
* __eq__
* __ne__
* add_new_information_from_process_object
* add_open_files
Input validation test:
* add_new_information_from_process_object
* add_open_files
* add_new_information
"""


def test_application_equality() -> None:
    """
    Test overloaded methods (== and !=).
    """
    first_application_name = "First application"
    second_application_name = "Second application"
    first_application = Application(process_name=first_application_name)
    second_application = Application(process_name=second_application_name)
    third_application = Application(process_name=first_application_name)

    # Check equality between Applications
    assert (first_application == third_application)
    assert (first_application != second_application)

    # Check equality between Application and string name
    assert (first_application_name == third_application)
    assert (first_application_name != second_application)


def test_add_new_information_from_process_with_input_validation() -> None:
    """
    Test input validation for adding new process information with process object.
    """
    process = next(psutil.process_iter())
    application = Application("Some application")

    # None process
    with pytest.raises(TypeError):
        # noinspection PyTypeChecker
        application.add_new_information_from_process_object(process=None,
                                                            data_retrieval_timestamp=datetime.datetime.now())
    # None data_retrieval_timestamp
    with pytest.raises(TypeError):
        # noinspection PyTypeChecker
        application.add_new_information_from_process_object(process=process,
                                                            data_retrieval_timestamp=None)
    # data_retrieval_timestamp with value set to tomorrow
    with pytest.raises(ValueError):
        tomorrow_date = datetime.date.today() + datetime.timedelta(days=1)
        tomorrow_datetime = datetime.datetime.combine(tomorrow_date, datetime.time.min)
        application.add_new_information_from_process_object(process=process,
                                                            data_retrieval_timestamp=tomorrow_datetime)


def test_add_new_information_from_process() -> None:
    """
    Test adding new application information from process.
    """
    processes = psutil.process_iter()
    retrieval_time = datetime.datetime.now()
    number_of_processes_checked = 0
    count = 0
    for process in processes:
        if count >= 5 and number_of_processes_checked > 0:
            break
        process_name = process.name()
        application = Application(process_name=process_name)
        try:
            application.add_new_information_from_process_object(process=process,
                                                                data_retrieval_timestamp=retrieval_time)
            assert (len(application.get_users()) > 0)
            assert (process_name == application.get_application_name())
            assert (len(application.get_open_files().keys()) >= 0)  # A process may or may not open a file
            assert (len(application.get_memory_usages()) > 0)
            assert (len(application.get_cpu_percentages()) > 0)
            assert (len(
                application.get_child_processes_count()) >= 0)  # A process may or may not have children processes
            assert (len(application.get_data_retrieval_timestamp()) == 1)
            assert (application.get_data_retrieval_timestamp()[0] == retrieval_time)
            number_of_processes_checked += 1
        except AccessDenied:  # Permission error if test is not run as admin.
            continue
        count += 1
    print("Number of processes checked: " + str(number_of_processes_checked))


# noinspection PyTypeChecker
def test_add_information_with_input_validation() -> None:
    """
    Test add information with input validation.
    """
    application = Application("Some application")

    # Invalid type for memory_usage
    with pytest.raises(TypeError):
        application.add_new_information(memory_usage=None, child_processes_count=1, users=set(),
                                        data_retrieval_timestamp=datetime.datetime.now(), cpu_percentage=0.98,
                                        open_files=list())
    # Invalid type for child_processes_count
    with pytest.raises(TypeError):
        application.add_new_information(memory_usage=1, child_processes_count=None, users=set(),
                                        data_retrieval_timestamp=datetime.datetime.now(), cpu_percentage=0.98,
                                        open_files=list())
    # Invalid type for users
    with pytest.raises(TypeError):
        application.add_new_information(memory_usage=1, child_processes_count=1, users=None,
                                        data_retrieval_timestamp=datetime.datetime.now(), cpu_percentage=0.98,
                                        open_files=list())

    # Invalid type for data_retrieval_timestamp
    with pytest.raises(TypeError):
        application.add_new_information(memory_usage=1, child_processes_count=0, users=set(),
                                        data_retrieval_timestamp=None, cpu_percentage=0.98,
                                        open_files=list())

    # Invalid type for cpu_percentage
    with pytest.raises(TypeError):
        application.add_new_information(memory_usage=1, child_processes_count=1, users=set(),
                                        data_retrieval_timestamp=datetime.datetime.now(), cpu_percentage="",
                                        open_files=list())
    # Invalid type for open_files
    with pytest.raises(TypeError):
        application.add_new_information(memory_usage=1, child_processes_count=0, users=set(),
                                        data_retrieval_timestamp=datetime.datetime.now(), cpu_percentage=0.98,
                                        open_files=None)
    # Negative value for memory_usage
    with pytest.raises(ValueError):
        application.add_new_information(memory_usage=-1, child_processes_count=1, users=set(),
                                        data_retrieval_timestamp=datetime.datetime.now(), cpu_percentage=0.98,
                                        open_files=list())

    # Negative value for child_processes_count
    with pytest.raises(ValueError):
        application.add_new_information(memory_usage=1, child_processes_count=-1, users=set(),
                                        data_retrieval_timestamp=datetime.datetime.now(), cpu_percentage=0.98,
                                        open_files=list())

    # Negative value for cpu_percentage
    with pytest.raises(ValueError):
        application.add_new_information(memory_usage=1, child_processes_count=1, users=set(),
                                        data_retrieval_timestamp=datetime.datetime.now(), cpu_percentage=-0.5,
                                        open_files=list())
    # data_retrieval_timestamp with value set to tomorrow
    with pytest.raises(ValueError):
        tomorrow_date = datetime.date.today() + datetime.timedelta(days=1)
        tomorrow_datetime = datetime.datetime.combine(tomorrow_date, datetime.time.min)
        application.add_new_information(memory_usage=1, child_processes_count=1, users=set(),
                                        data_retrieval_timestamp=tomorrow_datetime, cpu_percentage=-0.5,
                                        open_files=list())


def test_add_open_files_with_input_validation() -> None:
    """
    Test add open files with input validation.
    """
    application = Application("Some application")

    # None open_files
    with pytest.raises(TypeError):
        # noinspection PyTypeChecker
        application.add_open_files(open_files=None)

    # Invalid type for open_files
    with pytest.raises(TypeError):
        # noinspection PyTypeChecker
        application.add_open_files(open_files="")


def test_add_open_files() -> None:
    """
    Test add open files for each application.
    """
    processes = psutil.process_iter()
    number_of_processes_checked = 0
    for process in processes:
        if number_of_processes_checked > 0:
            break
        process_name = process.name()
        application = Application(process_name=process_name)
        try:
            process_open_files = process.open_files()
            application.add_open_files(process_open_files)
            application_open_files = application.get_open_files()
            assert (len(process_open_files) == len(application_open_files.keys()))

            for open_file in process_open_files:
                assert open_file.path in application_open_files
                if hasattr(open_file, "mode"):  # For Linux. Some OS don't have mode attribute.
                    assert open_file.mode in application_open_files[open_file.path]
        except AccessDenied:  # Permission error if test is not run as admin.
            continue
        except OSError:
            continue
    print("Number of processes checked: " + str(number_of_processes_checked))


def test_cpu_percent_value_when_adding_process_object_to_application_profile() -> None:
    """
    Test that getting cpu_percent when adding processes to an application profile is not always 0.0
    """
    processes = psutil.process_iter()
    number_of_ps_with_non_zero_cpu_usage = 0  # Some applications may have 0.0 of cpu usage
    for process in processes:
        application = Application("Some application")
        try:
            application.add_new_information_from_process_object(process=process,
                                                                data_retrieval_timestamp=datetime.datetime.now())
        except (psutil.NoSuchProcess, psutil.ZombieProcess, psutil.AccessDenied):
            continue

        if all(cpu_percentage >= 0.0 for cpu_percentage in application.get_cpu_percentages()):
            number_of_ps_with_non_zero_cpu_usage += 1
    assert number_of_ps_with_non_zero_cpu_usage > 0
