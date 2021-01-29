import shutil
from typing import Dict

import pytest

from paths import SAMPLE_APP_PROF_DATA_PATH, LOGGER_TEST_DIR_PATH, TEST_APP_PROF_DATA_DIR_PATH
from src.main.psHandler.AppProfileDataManager import AppProfileDataManager
from src.utils.error_messages import empty_collection_message


@pytest.fixture(scope="module")
def saved_test_app_profiles_dict() -> Dict[str, dict]:
    """
    pytest fixture for retrieving the test app profiles as a dictionaries.
    :raises ValueError if the test profiles retrieved are empty.
    :return: The test app profiles.
    :rtype: Dict[str, dict]
    """

    saved_test_app_profiles_dict = AppProfileDataManager.get_saved_profiles_as_dict(SAMPLE_APP_PROF_DATA_PATH)
    if len(saved_test_app_profiles_dict) == 0:
        raise ValueError(empty_collection_message.format("saved_test_app_profiles_dict"))
    return saved_test_app_profiles_dict


@pytest.fixture(scope="session", autouse=True)
def remove_all_create_files() -> None:
    """
    Cleans up all the directories created for testing.
    """
    yield
    directories_to_remove =[LOGGER_TEST_DIR_PATH, TEST_APP_PROF_DATA_DIR_PATH]
    for directory_to_remove in directories_to_remove:
        shutil.rmtree(directory_to_remove)
