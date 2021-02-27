import shutil
import pytest

import wades_config
from paths import LOGGER_TEST_DIR_PATH, TEST_APP_PROF_DATA_DIR_PATH, TEST_WADES_DIR_PATH


@pytest.fixture
def setup_and_clean_up_modelling_requirements() -> None:
    """
    Sets up and cleans up the modelling requirements by changing the is_modelling value to true and minimum modelling
    size to 3.
    """
    is_modelling = wades_config.is_modelling
    wades_config.is_modelling = True
    minimum_retrieval_size_for_modelling = wades_config.minimum_retrieval_size_for_modelling
    wades_config.minimum_retrieval_size_for_modelling = 3
    yield
    wades_config.is_modelling = is_modelling
    wades_config.minimum_retrieval_size_for_modelling = minimum_retrieval_size_for_modelling


@pytest.fixture(scope="session", autouse=True)
def setup_all_tests() -> None:
    """
    Sets up all the test. This is executed before/after all tests. Changes the values of wades_config.is_test to True,
    and after all test are run, it cleans the target path and changes the wades_config.is_test back to its original
    state.
    """
    is_test = wades_config.is_test
    wades_config.is_test = True
    yield
    wades_config.is_test = is_test
    shutil.rmtree(TEST_WADES_DIR_PATH)


@pytest.fixture(scope="function", autouse=True)
def setup_each_tests() -> None:
    """
    Sets up each test. It is executes before/after each test. After each test is run, clears the target path so it does
    not affect the following tests.
    """
    yield
    directories_to_remove = [LOGGER_TEST_DIR_PATH, TEST_APP_PROF_DATA_DIR_PATH]
    for directory_to_remove in directories_to_remove:
        shutil.rmtree(directory_to_remove)
    LOGGER_TEST_DIR_PATH.mkdir(parents=True, exist_ok=True)
    TEST_APP_PROF_DATA_DIR_PATH.mkdir(parents=True, exist_ok=True)
