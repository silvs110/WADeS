import pathlib

ROOT_PATH = pathlib.Path(__file__).parent.absolute()
APP_PROF_DATA_PATH = ROOT_PATH / "data" / "app_profiles"
APP_PROF_DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
SAMPLE_APP_PROF_DATA_PATH = ROOT_PATH / "src/tests/sample_data/sample_app_profile_data"
