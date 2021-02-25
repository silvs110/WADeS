import pytest
from numpy import nan

import paths
from paths import SAMPLE_APP_PROF_DATA_PATH, TEST_APP_PROF_DATA_FILE_PATH, \
    TEST_RETRIEVAL_TIMESTAMP_FILE_PATH
from src.main.common.AppProfile import AppProfile
from src.main.common.enum.AppProfileAttribute import AppProfileAttribute
from src.main.common.enum.AppSummaryAttribute import AppSummaryAttribute
from src.main.modeller.FrequencyTechnique import FrequencyTechnique
from src.main.psHandler.AppProfileDataManager import AppProfileDataManager
from src.main.psHandler.ProcessHandler import ProcessHandler
from src.tests.test_helpers import check_app_profile_has_the_right_format

"""
Contains tests for AppProfileDataManager class

Functional tests:
* save_app_profiles()
* get_saved_profiles()
* get_saved_profiles_as_dict()

Input Validation tests:
* save_app_profiles()
* get_saved_profiles()
* get_saved_profiles_as_dict()
"""

logger_name = "testAppProfileDataManager"


# noinspection PyTypeChecker
def test_save_app_profiles_with_input_validation() -> None:
    """
    Test save_app_profiles() with input validation.
    Checks that an exception is thrown when an invalid input is provided.
    """
    # None input for app_profiles
    with pytest.raises(TypeError):
        AppProfileDataManager.save_app_profiles(app_profiles=None)

    # Empty string input for app_profiles
    with pytest.raises(TypeError):
        AppProfileDataManager.save_app_profiles(app_profiles="")

    # Invalid elements in list as input for app_profiles
    with pytest.raises(TypeError):
        AppProfileDataManager.save_app_profiles(app_profiles=["!2", "error"])

    with pytest.raises(TypeError):
        AppProfileDataManager.save_app_profiles(app_profiles=[2, 7])

    # None input for app_profile_file
    with pytest.raises(TypeError):
        AppProfileDataManager.save_app_profiles(app_profiles=list(), app_profile_file_path=None)

    # Invalid input type for app_profile_file
    with pytest.raises(TypeError):
        AppProfileDataManager.save_app_profiles(app_profiles=list(), app_profile_file_path=5)


def test_save_and_get_profile_data() -> None:
    """
    Test save_app_profiles() and get_saved_profiles().
    Checks that saving and retrieving the app profiles does not modify the data.
    """

    process_handler = ProcessHandler(logger_name, True)
    process_handler.collect_running_processes_information()
    actual_app_profiles = process_handler.get_registered_app_profiles_list()
    latest_retrieved_data_timestamp = process_handler.get_latest_retrieved_data_timestamp()
    AppProfileDataManager.save_app_profiles(app_profiles=actual_app_profiles,
                                            app_profile_file_path=TEST_APP_PROF_DATA_FILE_PATH,
                                            retrieval_timestamp_file_path=TEST_RETRIEVAL_TIMESTAMP_FILE_PATH,
                                            retrieval_timestamp=latest_retrieved_data_timestamp)

    expected_app_profiles = AppProfileDataManager.get_saved_profiles(app_profile_file=TEST_APP_PROF_DATA_FILE_PATH)
    TEST_APP_PROF_DATA_FILE_PATH.unlink()

    saved_retrieved_timestamp = AppProfileDataManager.get_last_retrieved_data_timestamp(
        retrieval_timestamp_file_path=TEST_RETRIEVAL_TIMESTAMP_FILE_PATH)

    assert latest_retrieved_data_timestamp == saved_retrieved_timestamp
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
        expected_opened_files = expected_app_profile_dict.pop(AppProfileAttribute.opened_files.name)
        actual_opened_files = actual_app_profile_dict.pop(AppProfileAttribute.opened_files.name)
        assert expected_opened_files == actual_opened_files

        assert expected_app_profile_dict == actual_app_profile_dict


def test_get_app_profile_as_dict_with_valid_input() -> None:
    """
    Test get_saved_profiles_as_dict().
    Checks that get_saved_profiles_as_dict() can retrieve app_profiles as dict in the right format.
    """
    app_name = "common_case_app"
    app_profiles = AppProfileDataManager.get_saved_profiles_as_dict(SAMPLE_APP_PROF_DATA_PATH)
    app_profile_attribute_names = {enum.name for enum in AppProfileAttribute}

    assert isinstance(app_profiles, dict)
    assert len(app_profiles) > 0

    app_profile = app_profiles[app_name]
    actual_app_profile_attrs = app_profile.keys()
    assert actual_app_profile_attrs == app_profile_attribute_names

    check_app_profile_has_the_right_format(app_name, app_profile)


# noinspection PyTypeChecker
def test_get_app_profile_as_dict_with_invalid_input() -> None:
    """
    Test get_saved_profiles_as_dict() with invalid inputs.
    Checks that an exception is thrown when an invalid input is provided.
    """
    # None input for app_profile_file
    with pytest.raises(TypeError):
        AppProfileDataManager.get_saved_profiles_as_dict(app_profile_file=None)

    # Invalid input type for app_profile_file
    with pytest.raises(TypeError):
        AppProfileDataManager.get_saved_profiles_as_dict(app_profile_file=5)


# noinspection PyTypeChecker
def test_get_app_profile_with_invalid_input() -> None:
    """
    Test get_saved_profiles() with invalid inputs.
    Checks that an exception is thrown when an invalid input is provided.
    """
    # None input for app_profile_file
    with pytest.raises(TypeError):
        AppProfileDataManager.get_saved_profiles(app_profile_file=None)

    # Invalid input type for app_profile_file
    with pytest.raises(TypeError):
        AppProfileDataManager.get_saved_profiles(app_profile_file=5)


def test_save_and_get_abnormal_apps_from_file() -> None:
    """
    Test saving and getting abnormal apps from a file is in the correct format and has the right values.
    """
    saved_app_profile = AppProfileDataManager.get_saved_profiles(paths.SAMPLE_APP_PROF_DATA_PATH)
    ft = FrequencyTechnique()
    modelled_apps = ft(saved_app_profile)
    # Note: Some of the saved app profiles are not anomalous, however this test verifies that they are saved in correct
    # format.
    AppProfileDataManager.save_abnormal_apps(modelled_apps, paths.TEST_APP_ANOM_FILE_PATH)

    actual_saved_abnormal_apps = AppProfileDataManager.get_saved_abnormal_apps(paths.TEST_APP_ANOM_FILE_PATH)
    expected_saved_abnormal_apps = dict()
    for modelled_app in modelled_apps:
        app_name = modelled_app.get_app_name()
        abnormal_attrs = list(modelled_app.get_abnormal_attrs())
        risk_level = modelled_app.get_risk_level()
        error_message = modelled_app.get_error_message()
        latest_retrieved_timestamp = modelled_app.get_latest_retrieved_app_details() \
            [AppProfileAttribute.data_retrieval_timestamps.name][0]
        if app_name not in expected_saved_abnormal_apps:
            expected_saved_abnormal_apps[app_name] = list()
        abnormal_app_saved_entries = {
            AppSummaryAttribute.abnormal_attributes.name: set(abnormal_attrs),
            AppSummaryAttribute.risk.name: risk_level.name,
            AppSummaryAttribute.error_message.name: error_message if error_message is not None else nan,
            AppProfileAttribute.data_retrieval_timestamps.name: latest_retrieved_timestamp
        }
        expected_saved_abnormal_apps[app_name].append(abnormal_app_saved_entries)

    # Changing the abnormal attribute values to set as during modelling the order of those values may change.
    for saved_abnormal_app in actual_saved_abnormal_apps.values():
        for abnormal_entry in saved_abnormal_app:
            # noinspection PyTypeChecker
            abnormal_entry[AppSummaryAttribute.abnormal_attributes.name] = \
                set(abnormal_entry[AppSummaryAttribute.abnormal_attributes.name])

    assert expected_saved_abnormal_apps == actual_saved_abnormal_apps
