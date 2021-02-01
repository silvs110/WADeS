import pathlib

from wades_config import app_profile_file_name, retrieval_timestamp_file_name, abnormal_apps_file_name

# TEST PATH
ROOT_PATH = pathlib.Path(__file__).parent.absolute()
TEST_APP_PROF_DATA_DIR_PATH = ROOT_PATH / "data"
TEST_APP_PROF_DATA_DIR_PATH.mkdir(parents=True, exist_ok=True)
TEST_APP_PROF_DATA_FILE_PATH = TEST_APP_PROF_DATA_DIR_PATH / app_profile_file_name
TEST_APP_ANOM_FILE_PATH = TEST_APP_PROF_DATA_DIR_PATH / abnormal_apps_file_name
SAMPLE_APP_PROF_DATA_PATH = ROOT_PATH / "src/tests/sample_data/sample_app_profile_data.csv"
LOGGER_TEST_DIR_PATH = ROOT_PATH / "log"
LOGGER_TEST_DIR_PATH.mkdir(parents=True, exist_ok=True)
TEST_RETRIEVAL_TIMESTAMP_FILE_PATH = TEST_APP_PROF_DATA_DIR_PATH / retrieval_timestamp_file_name

# NON-TEST PATHS
WADES_DIR_PATH = pathlib.Path.home() / ".wades"
WADES_DIR_PATH.mkdir(parents=True, exist_ok=True)
APP_PROF_DATA_DIR_PATH = WADES_DIR_PATH / "data"
APP_PROF_DATA_DIR_PATH.mkdir(parents=True, exist_ok=True)
APP_PROF_DATA_FILE_PATH = APP_PROF_DATA_DIR_PATH / app_profile_file_name
APP_ANOM_FILE_PATH = APP_PROF_DATA_DIR_PATH / abnormal_apps_file_name
PID_FILES_DIR_PATH = WADES_DIR_PATH / "run"
PID_FILES_DIR_PATH.mkdir(parents=True, exist_ok=True)
LOGGER_DIR_PATH = WADES_DIR_PATH / "log"
LOGGER_DIR_PATH.mkdir(parents=True, exist_ok=True)
RETRIEVAL_TIMESTAMP_FILE_PATH = APP_PROF_DATA_DIR_PATH / retrieval_timestamp_file_name
