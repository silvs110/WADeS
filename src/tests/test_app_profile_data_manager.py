import pytest

from src.main.AppProfile import AppProfile
from src.main.AppProfileAttribute import AppProfileAttribute
from src.main.AppProfileDataManager import AppProfileDataManager
from src.main.ProcessHandler import ProcessHandler

"""
Contains tests for AppProfileDataManager class

Functional tests:
* save_app_profiles()
* save_app_profiles()

Input Validation tests:
* save_app_profiles()

"""


# noinspection PyTypeChecker
def test_save_app_profiles_with_input_validation() -> None:
    """
    Test save_app_profiles() with input validation.
    """
    # None type as input
    with pytest.raises(TypeError):
        AppProfileDataManager.save_app_profiles(app_profiles=None)

    # Empty string as input
    with pytest.raises(TypeError):
        AppProfileDataManager.save_app_profiles(app_profiles="")

    # Invalid elements in list as input
    with pytest.raises(TypeError):
        AppProfileDataManager.save_app_profiles(app_profiles=["!2", "error"])

    with pytest.raises(TypeError):
        AppProfileDataManager.save_app_profiles(app_profiles=[2, 7])


def test_save_and_get_profile_data() -> None:
    """
    Test save_app_profiles() and get_saved_profiles().
    """
    process_handler = ProcessHandler()
    process_handler.collect_running_processes_information()
    actual_app_profiles = process_handler.get_registered_app_profiles_list()

    AppProfileDataManager.save_app_profiles(app_profiles=actual_app_profiles)
    expected_app_profiles = AppProfileDataManager.get_saved_profiles()
    assert len(expected_app_profiles) == len(actual_app_profiles)
    for index in range(0, len(expected_app_profiles)):
        expected_app_profile = expected_app_profiles[index]
        actual_app_profile = actual_app_profiles[index]

        assert (isinstance(actual_app_profile, AppProfile) and isinstance(expected_app_profile, AppProfile))
        expected_app_profile_dict = expected_app_profile.dict_format()
        actual_app_profile_dict = actual_app_profile.dict_format()

        # Removing attributes which order doesn't matter (opened_files and usernames)
        expected_usernames = expected_app_profile_dict.pop(AppProfileAttribute.usernames.name)
        actual_usernames = actual_app_profile_dict.pop(AppProfileAttribute.usernames.name)
        assert set(expected_usernames) == set(actual_usernames)
        expected_opened_files_raw = expected_app_profile_dict.pop(AppProfileAttribute.opened_files.name)
        expected_opened_files = {path: set(permissions) for path, permissions in expected_opened_files_raw.items()}
        actual_opened_files_raw = actual_app_profile_dict.pop(AppProfileAttribute.opened_files.name)
        actual_opened_files = {path: set(permissions) for path, permissions in actual_opened_files_raw.items()}
        assert expected_opened_files == actual_opened_files

        assert expected_app_profile_dict == actual_app_profile_dict
