from datetime import datetime

import pytest
from numpy import nan

import paths
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
    timestamp = datetime.now()
    # None input for app_profiles
    with pytest.raises(TypeError):
        AppProfileDataManager.save_app_profiles(app_profiles=None, retrieval_timestamp=timestamp)

    # Empty string input for app_profiles
    with pytest.raises(TypeError):
        AppProfileDataManager.save_app_profiles(app_profiles="", retrieval_timestamp=timestamp)

    # Invalid elements in list as input for app_profiles
    with pytest.raises(TypeError):
        AppProfileDataManager.save_app_profiles(app_profiles=["!2", "error"], retrieval_timestamp=timestamp)

    with pytest.raises(TypeError):
        AppProfileDataManager.save_app_profiles(app_profiles=[2, 7], retrieval_timestamp=timestamp)

    # None input for app_profile_file
    with pytest.raises(TypeError):
        AppProfileDataManager.save_app_profiles(app_profiles=list(), retrieval_timestamp=timestamp,
                                                app_profile_base_dir=None)

    # Invalid input type for app_profile_file
    with pytest.raises(TypeError):
        AppProfileDataManager.save_app_profiles(app_profiles=list(), retrieval_timestamp=timestamp,
                                                app_profile_base_dir=5)

    # None input for app_profile_file
    with pytest.raises(TypeError):
        AppProfileDataManager.save_app_profiles(app_profiles=list(), retrieval_timestamp=None)

    # Invalid input type for app_profile_file
    with pytest.raises(TypeError):
        AppProfileDataManager.save_app_profiles(app_profiles=list(), retrieval_timestamp="wew")


def test_save_and_get_profile_data() -> None:
    """
    Test save_app_profiles() and get_saved_profiles().
    Checks that saving and retrieving the app profiles does not modify the data.
    """

    process_handler = ProcessHandler(logger_name)
    process_handler.collect_running_processes_information()

    latest_retrieved_data_timestamp = process_handler.get_latest_retrieved_data_timestamp()

    app_name = "systemd"
    expected_app_profiles = AppProfileDataManager.get_saved_profile(app_name)

    saved_retrieved_timestamp = AppProfileDataManager.get_last_retrieved_data_timestamp()

    assert isinstance(expected_app_profiles, AppProfile)
    assert latest_retrieved_data_timestamp == saved_retrieved_timestamp


def test_get_app_profile_as_dict_with_valid_input() -> None:
    """
    Test get_saved_profiles_as_dict().
    Checks that get_saved_profiles_as_dict() can retrieve app_profiles as dict in the right format.
    """
    app_name = "common_case_app"
    app_profile_dict = AppProfileDataManager.get_saved_profile_as_dict(app_name, paths.SAMPLE_APP_PROF_DATA_PATH)
    app_profile_attribute_names = {enum.name for enum in AppProfileAttribute}

    assert isinstance(app_profile_dict, dict)
    assert len(app_profile_dict) > 0

    actual_app_profile_attrs = app_profile_dict.keys()
    assert actual_app_profile_attrs == app_profile_attribute_names

    check_app_profile_has_the_right_format(app_name, app_profile_dict)


# noinspection PyTypeChecker
def test_get_app_profile_as_dict_with_invalid_input() -> None:
    """
    Test get_saved_profiles_as_dict() with invalid inputs.
    Checks that an exception is thrown when an invalid input is provided.
    """
    # None input for app_profile_name
    with pytest.raises(TypeError):
        AppProfileDataManager.get_saved_profile_as_dict(app_profile_name=None)

    # Invalid input type for app_profile_name
    with pytest.raises(TypeError):
        AppProfileDataManager.get_saved_profile_as_dict(app_profile_name=5)

    # None input for app_profile_base
    with pytest.raises(TypeError):
        AppProfileDataManager.get_saved_profile_as_dict(app_profile_name="app", base_path=None)

    # Invalid input type for app_profile_name
    with pytest.raises(TypeError):
        AppProfileDataManager.get_saved_profile_as_dict(app_profile_name="app", base_path=5)


# noinspection PyTypeChecker
def test_get_app_profile_with_invalid_input() -> None:
    """
    Test get_saved_profiles() with invalid inputs.
    Checks that an exception is thrown when an invalid input is provided.
    """
    # None input for app_profile_file
    with pytest.raises(TypeError):
        AppProfileDataManager.get_saved_profile(app_profile_name=None)

    # Invalid input type for app_profile_file
    with pytest.raises(TypeError):
        AppProfileDataManager.get_saved_profile(app_profile_name=5)


def test_save_and_get_abnormal_apps_from_file() -> None:
    """
    Test saving and getting abnormal apps from a file is in the correct format and has the right values.
    """
    app_profiles = list()
    app_names = ["common_case_app", "app_with_high_risk_and_low_risk_anomaly", "app_with_blacklisted_file"]
    for app_name in app_names:
        saved_app_profile = AppProfileDataManager.get_saved_profile(app_name, paths.SAMPLE_APP_PROF_DATA_PATH)
        app_profiles.append(saved_app_profile)
    ft = FrequencyTechnique()
    modelled_apps = ft(app_profiles)
    # Note: Some of the saved app profiles are not anomalous, however this test assumes that they are
    # and verifies that they are saved in correct format.
    AppProfileDataManager.save_abnormal_apps(modelled_apps)

    actual_saved_abnormal_apps = AppProfileDataManager.get_saved_abnormal_apps()
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


def test_get_saved_application_names() -> None:
    """
    Tests get saved application names.
    """
    ps_handler = ProcessHandler()
    ps_handler.collect_running_processes_information()
    application_names = AppProfileDataManager.get_saved_app_profiles_names()
    assert len(application_names) > 0
    assert "systemd" in application_names
    # save_last_retrieved_data_timestamp


# noinspection PyTypeChecker
def test_get_saved_application_names_with_invalid_inputs() -> None:
    """
    Tests get saved application names with invalid base directory.
    """
    # None base path
    with pytest.raises(TypeError):
        AppProfileDataManager.get_saved_app_profiles_names(None)

    # Number base path
    with pytest.raises(TypeError):
        AppProfileDataManager.get_saved_app_profiles_names(7)


# noinspection PyTypeChecker
def test_save_last_retrieved_data_timestamp_with_invalid_inputs() -> None:
    """
    Tests saving last retrieved_data_timestamp with invalid inputs.
    """

    timestamp = datetime.now()

    # None retrieval_timestamp
    with pytest.raises(TypeError):
        AppProfileDataManager.save_last_retrieved_data_timestamp(retrieval_timestamp=None)

    # Numeric retrieval_timestamp
    with pytest.raises(TypeError):
        AppProfileDataManager.save_last_retrieved_data_timestamp(retrieval_timestamp=7)

    # None retrieval_timestamp_file_path
    with pytest.raises(TypeError):
        AppProfileDataManager.save_last_retrieved_data_timestamp(retrieval_timestamp=timestamp,
                                                                 retrieval_timestamp_file_path=None)
    # Invalid retrieval_timestamp_file_path
    with pytest.raises(TypeError):
        AppProfileDataManager.save_last_retrieved_data_timestamp(retrieval_timestamp=timestamp,
                                                                 retrieval_timestamp_file_path="sdjs")
