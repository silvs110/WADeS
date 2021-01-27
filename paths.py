import pathlib

ROOT_PATH = pathlib.Path(__file__).parent.absolute()
APP_PROF_DATA_DIR_PATH = ROOT_PATH / "data"
APP_PROF_DATA_DIR_PATH.mkdir(parents=True, exist_ok=True)
APP_PROF_DATA_FILE_PATH = APP_PROF_DATA_DIR_PATH / "app_profiles.csv"
SAMPLE_APP_PROF_DATA_PATH = ROOT_PATH / "src/tests/sample_data/sample_app_profile_data.csv"
LOGGER_TEST_DIR_PATH = ROOT_PATH / "log"
LOGGER_TEST_DIR_PATH.mkdir(parents=True, exist_ok=True)

WADES_DIR_PATH = pathlib.Path.home() / ".wades"
WADES_DIR_PATH.mkdir(parents=True, exist_ok=True)
LOGGER_DIR_PATH = WADES_DIR_PATH / "log"
LOGGER_DIR_PATH.mkdir(parents=True, exist_ok=True)