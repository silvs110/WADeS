import psutil
import pytest

from src.main.ProcessHandler import ProcessHandler

"""
This file contains test for ProcessHandler class.

Functional test for the following methods in Application class:
* collect_running_process_and_group_by_application

Input validation test:
* add_application_processes_to_application_profile
* add_application_processes_info_to_application_profile
* add_process_info_to_application_object
* collect_application_process_properties
* find_ppids_from_application_processes

Output Format test:
* collect_running_process_and_group_by_application
* collect_application_process_properties
"""


def test_collect_running_process_and_group_by_application_output_format() -> None:
    """
    Verify that collect_running_process_and_group_by_application output correct format.
    """
    process_handler = ProcessHandler()
    applications_to_processes_map = process_handler.collect_running_process_and_group_by_application()
    assert isinstance(applications_to_processes_map, dict)
    for application_name, application_processes in applications_to_processes_map.items():
        assert isinstance(application_name, str)
        assert isinstance(application_processes, dict)
        for pid, process in application_processes.items():
            assert isinstance(pid, int)
            assert isinstance(process, psutil.Process)


def test_collect_running_process_and_group_by_application() -> None:
    """
    Test collect_running_process_and_group_by_application group processes by application name.
    """
    process_handler = ProcessHandler()
    applications_to_processes_map = process_handler.collect_running_process_and_group_by_application()
    for application_name, application_processes in applications_to_processes_map.items():
        processes = application_processes.values()
        for process in processes:
            try:
                assert application_name == process.name()
            except (psutil.NoSuchProcess, psutil.ZombieProcess):
                continue


# noinspection PyTypeChecker
def test_add_application_processes_to_application_profile_with_invalid_inputs() -> None:
    """
    Test add_application_processes_to_application_profile using invalid inputs.
    """
    process_handler = ProcessHandler()
    # None input
    with pytest.raises(TypeError):
        process_handler.add_application_processes_to_application_profile(applications_dict=None)

    # Invalid dict values
    with pytest.raises(TypeError):
        process_handler.add_application_processes_to_application_profile(applications_dict={1: 2})

    # Invalid input
    with pytest.raises(TypeError):
        process_handler.add_application_processes_to_application_profile(applications_dict=3)


# noinspection PyTypeChecker
def test_add_application_processes_info_to_application_profile_with_invalid_inputs() -> None:
    """
    Test add_application_processes_info_to_application_profile using invalid inputs.
    """
    process_handler = ProcessHandler()
    # None input
    with pytest.raises(TypeError):
        process_handler.add_application_processes_info_to_application_profile(applications_dict=None)

    # Invalid dict values
    with pytest.raises(TypeError):
        process_handler.add_application_processes_info_to_application_profile(applications_dict={1: 2})

    # Invalid input
    with pytest.raises(TypeError):
        process_handler.add_application_processes_info_to_application_profile(applications_dict='')


# noinspection PyTypeChecker
def test_add_process_info_to_application_object_with_invalid_inputs() -> None:
    """
    Test add_process_info_to_application_object with invalid inputs.
    """
    process_handler = ProcessHandler()
    # None input
    with pytest.raises(TypeError):
        process_handler.add_process_to_application_profile(process=None)

    # Invalid input
    with pytest.raises(TypeError):
        process_handler.add_process_to_application_profile(process=dict())
    with pytest.raises(TypeError):
        process_handler.add_process_to_application_profile(process=1)


# noinspection PyTypeChecker
def test_collect_application_processes_properties_with_invalid_inputs() -> None:
    """
    Test collect_application_processes_properties with invalid inputs.
    """
    # None input
    with pytest.raises(TypeError):
        ProcessHandler.collect_application_processes_properties(processes=None)

    # Invalid list values
    with pytest.raises(TypeError):
        ProcessHandler.collect_application_processes_properties(processes=[1, 2])

    # Invalid input
    with pytest.raises(TypeError):
        ProcessHandler.collect_application_processes_properties(processes=2)


def test_collect_application_process_properties_with_different_app_processes() -> None:
    """
    Test collect_application_processes_properties with processes from different applications.
    """
    processes = list(psutil.process_iter())
    num_to_check = 10 if len(processes) >= 10 else len(processes)
    with pytest.raises(ValueError):
        ProcessHandler.collect_application_processes_properties(processes[:num_to_check])


def test_collect_application_process_properties_output_format() -> None:
    """
    Test collect_application_processes_properties.
    """
    expected_process_property_keys = {"open_files", "rss", "cpu_usage", "users"}
    process_handler = ProcessHandler()
    application_to_processes_map = process_handler.collect_running_process_and_group_by_application()
    num_to_check = 3 if len(application_to_processes_map.keys()) >= 3 else len(application_to_processes_map.keys())
    for application_processes in list(application_to_processes_map.values())[:num_to_check]:
        processes_list = list(application_processes.values())
        processes_properties = ProcessHandler.collect_application_processes_properties(processes_list)
        actual_processes_property_keys = set(processes_properties.keys())
        assert expected_process_property_keys == actual_processes_property_keys


# noinspection PyTypeChecker
def test_find_ppids_from_application_processes_with_invalid_inputs() -> None:
    """
    Test find_ppids_from_application_processes with invalid inputs.
    """
    # None input
    with pytest.raises(TypeError):
        ProcessHandler.find_ppids_from_application_processes(processes=None)

    # Invalid list values
    with pytest.raises(TypeError):
        ProcessHandler.find_ppids_from_application_processes(processes=[1, 2])

    # Invalid input
    with pytest.raises(TypeError):
        ProcessHandler.find_ppids_from_application_processes(processes=2)
