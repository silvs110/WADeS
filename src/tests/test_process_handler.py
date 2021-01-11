from src.main.common.AppProfile import AppProfile
from src.main.psHandler.ProcessHandler import ProcessHandler

"""
This file contains test for ProcessHandler class.

Functional test for the following methods in AppProfile class:
* collect_running_processes_information

Input validation test:

Output Format test:

"""


def test_collect_running_processes_information() -> None:
    """
    Test collecting running process information by checking that it sets the value to the registered application
    properties.
    """
    process_handler = ProcessHandler()
    registered_apps_before_collection = process_handler.get_registered_application_names()
    assert len(registered_apps_before_collection) == 0
    process_handler.collect_running_processes_information()
    registered_apps_after_collection = process_handler.get_registered_app_profiles_as_dict()
    registered_apps_names = registered_apps_after_collection.keys()
    assert len(registered_apps_names) > 1
    for app_profile in registered_apps_after_collection.values():
        assert isinstance(app_profile, AppProfile)
        data_retrieval_timestamps = app_profile.get_data_retrieval_timestamp()
        assert len(data_retrieval_timestamps) >= 1  # Some apps may have more than one process
        assert data_retrieval_timestamps[0] is not None
