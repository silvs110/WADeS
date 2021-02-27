import pathlib


# TEST PATH
import wades_config

ROOT_PATH = pathlib.Path(__file__).parent.absolute()
TEST_WADES_DIR_PATH = ROOT_PATH / "wades"
TEST_APP_PROF_DATA_DIR_PATH = TEST_WADES_DIR_PATH / "data"
SAMPLE_APP_PROF_DATA_PATH = ROOT_PATH / "src/tests/sample_data"
LOGGER_TEST_DIR_PATH = ROOT_PATH / "log"

# NON-TEST PATHS
WADES_DIR_PATH = pathlib.Path("/var/lib").absolute() / "wades"
APP_PROF_DATA_DIR_PATH = WADES_DIR_PATH / "data"
PID_FILES_DIR_PATH = WADES_DIR_PATH / "run"
LOGGER_DIR_PATH = WADES_DIR_PATH / "log"

if wades_config.is_test:
    TEST_APP_PROF_DATA_DIR_PATH.mkdir(parents=True, exist_ok=True)
    LOGGER_TEST_DIR_PATH.mkdir(parents=True, exist_ok=True)
else:
    WADES_DIR_PATH.mkdir(parents=True, exist_ok=True)
    APP_PROF_DATA_DIR_PATH.mkdir(parents=True, exist_ok=True)
    PID_FILES_DIR_PATH.mkdir(parents=True, exist_ok=True)
    LOGGER_DIR_PATH.mkdir(parents=True, exist_ok=True)
