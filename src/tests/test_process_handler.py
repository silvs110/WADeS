from src.main.common.AppProfile import AppProfile
from src.main.psHandler.AppProfileDataManager import AppProfileDataManager
from src.main.psHandler.ProcessHandler import ProcessHandler

"""
This file contains test for ProcessHandler class.

Functional test for the following methods in AppProfile class:
* collect_running_processes_information

Input validation test:

Output Format test:

"""

logger_name = "testProcessHandler"


def test_collect_running_processes_information() -> None:
    """
    Test collecting running process information by checking that it sets the value to the registered application
    properties.
    """
    common_app_names = ["systemd", "kthreadd", "rcu_gp"]
    process_handler = ProcessHandler(logger_name)
    for common_app_name in common_app_names:
        app_profile = AppProfileDataManager.get_saved_profile(common_app_name)
        assert app_profile is None
    process_handler.collect_running_processes_information()

    for common_app_name in common_app_names:
        app_profile = AppProfileDataManager.get_saved_profile(common_app_name)
        assert isinstance(app_profile, AppProfile)
        data_retrieval_timestamps = app_profile.get_data_retrieval_timestamps()
        assert len(data_retrieval_timestamps) >= 1  # Some apps may have more than one process
        assert data_retrieval_timestamps[0] is not None
