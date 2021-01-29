import datetime

import psutil
import pytest
from psutil import AccessDenied

from paths import SAMPLE_APP_PROF_DATA_PATH
import wades_config
from src.main.common.AppProfile import AppProfile
from src.main.common.enum.AppProfileAttribute import AppProfileAttribute
from src.main.psHandler.AppProfileDataManager import AppProfileDataManager
from src.main.psHandler.ProcessHandler import ProcessHandler
from src.tests.test_helpers import check_app_profile_has_the_right_format

"""
This file contains test for AppProfile class.
Functional test for the following methods in AppProfile class:
* __eq__()
* __ne__()
* add_new_information_from_process_object()
* add_open_files()
* dict_format()
* get_previously_retrieved_data()
* get_latest_retrieved_data()

Input validation test:
* add_new_information_from_process_object()
* add_open_files()
* add_new_information()
* set_value_from_dict()

"""

logger_name = "testAppProfile"


def test_application_equality() -> None:
    """
    Test overloaded methods (== and !=).
    """
    first_application_name = "First application"
    second_application_name = "Second application"
    first_application = AppProfile(application_name=first_application_name)
    second_application = AppProfile(application_name=second_application_name)
    third_application = AppProfile(application_name=first_application_name)

    # Check equality between AppProfiles
    assert (first_application == third_application)
    assert (first_application != second_application)

    # Check equality between AppProfile and string name
    assert (first_application_name == third_application)
    assert (first_application_name != second_application)


def test_add_new_information_from_process_with_input_validation() -> None:
    """
    Test input validation for adding new process information with process object.
    """
    process = next(psutil.process_iter())
    app_profile = AppProfile("Some application")

    # None process
    with pytest.raises(TypeError):
        # noinspection PyTypeChecker
        app_profile.add_new_information_from_process_object(process=None,
                                                            data_retrieval_timestamp=datetime.datetime.now())
    # None data_retrieval_timestamp
    with pytest.raises(TypeError):
        # noinspection PyTypeChecker
        app_profile.add_new_information_from_process_object(process=process,
                                                            data_retrieval_timestamp=None)
    # data_retrieval_timestamp with value set to tomorrow
    with pytest.raises(ValueError):
        tomorrow_date = datetime.date.today() + datetime.timedelta(days=1)
        tomorrow_datetime = datetime.datetime.combine(tomorrow_date, datetime.time.min)
        app_profile.add_new_information_from_process_object(process=process,
                                                            data_retrieval_timestamp=tomorrow_datetime)


def test_add_new_information_from_process() -> None:
    """
    Test adding new application information from process.
    """
    processes = psutil.process_iter()
    retrieval_time = datetime.datetime.now()
    number_of_processes_checked = 0
    count = 0
    for process in processes:
        if count >= 5 and number_of_processes_checked > 0:
            break
        process_name = process.name()
        app_profile = AppProfile(application_name=process_name)
        try:
            app_profile.add_new_information_from_process_object(process=process,
                                                                data_retrieval_timestamp=retrieval_time)
            assert (len(app_profile.get_users()) > 0)
            assert (process_name == app_profile.get_application_name())
            assert (len(app_profile.get_open_files()) >= 0)  # A process may or may not open a file
            assert (len(app_profile.get_memory_usages()) > 0)
            assert (len(app_profile.get_cpu_percentages()) > 0)
            assert (len(
                app_profile.get_child_processes_count()) >= 0)  # A process may or may not have children processes
            assert (len(app_profile.get_data_retrieval_timestamps()) == 1)
            assert (app_profile.get_data_retrieval_timestamps()[0] == retrieval_time)
            number_of_processes_checked += 1
        except AccessDenied:  # Permission error if test is not run as admin.
            continue
        count += 1
    print("Number of processes checked: " + str(number_of_processes_checked))


# noinspection PyTypeChecker
def test_add_information_with_input_validation() -> None:
    """
    Test add information with input validation.
    """
    app_profile = AppProfile("Some application")

    # Invalid type for memory_usage
    with pytest.raises(TypeError):
        app_profile.add_new_information(memory_usage=None, child_processes_count=1, users=list(),
                                        data_retrieval_timestamp=datetime.datetime.now(), cpu_percentage=0.98,
                                        open_files=list())
    # Invalid type for child_processes_count
    with pytest.raises(TypeError):
        app_profile.add_new_information(memory_usage=1, child_processes_count=None, users=list(),
                                        data_retrieval_timestamp=datetime.datetime.now(), cpu_percentage=0.98,
                                        open_files=list())
    # Invalid type for users
    with pytest.raises(TypeError):
        app_profile.add_new_information(memory_usage=1, child_processes_count=1, users=None,
                                        data_retrieval_timestamp=datetime.datetime.now(), cpu_percentage=0.98,
                                        open_files=list())

    # Invalid type for data_retrieval_timestamp
    with pytest.raises(TypeError):
        app_profile.add_new_information(memory_usage=1, child_processes_count=0, users=list(),
                                        data_retrieval_timestamp=None, cpu_percentage=0.98,
                                        open_files=list())

    # Invalid type for cpu_percentage
    with pytest.raises(TypeError):
        app_profile.add_new_information(memory_usage=1, child_processes_count=1, users=list(),
                                        data_retrieval_timestamp=datetime.datetime.now(), cpu_percentage="",
                                        open_files=list())
    # Invalid type for open_files
    with pytest.raises(TypeError):
        app_profile.add_new_information(memory_usage=1, child_processes_count=0, users=list(),
                                        data_retrieval_timestamp=datetime.datetime.now(), cpu_percentage=0.98,
                                        open_files=None)
    # Negative value for memory_usage
    with pytest.raises(ValueError):
        app_profile.add_new_information(memory_usage=-1, child_processes_count=1, users=list(),
                                        data_retrieval_timestamp=datetime.datetime.now(), cpu_percentage=0.98,
                                        open_files=list())

    # Negative value for child_processes_count
    with pytest.raises(ValueError):
        app_profile.add_new_information(memory_usage=1, child_processes_count=-1, users=list(),
                                        data_retrieval_timestamp=datetime.datetime.now(), cpu_percentage=0.98,
                                        open_files=list())

    # Negative value for cpu_percentage
    with pytest.raises(ValueError):
        app_profile.add_new_information(memory_usage=1, child_processes_count=1, users=list(),
                                        data_retrieval_timestamp=datetime.datetime.now(), cpu_percentage=-0.5,
                                        open_files=list())
    # data_retrieval_timestamp with value set to tomorrow
    with pytest.raises(ValueError):
        tomorrow_date = datetime.date.today() + datetime.timedelta(days=1)
        tomorrow_datetime = datetime.datetime.combine(tomorrow_date, datetime.time.min)
        app_profile.add_new_information(memory_usage=1, child_processes_count=1, users=list(),
                                        data_retrieval_timestamp=tomorrow_datetime, cpu_percentage=-0.5,
                                        open_files=list())


def test_add_open_files_with_input_validation() -> None:
    """
    Test add open files with input validation.
    """
    app_profile = AppProfile("Some application")

    # None open_files
    with pytest.raises(TypeError):
        # noinspection PyTypeChecker
        app_profile.add_open_files(open_files=None, data_retrieval_timestamp=datetime.datetime.now())

    # Invalid type for open_files
    with pytest.raises(TypeError):
        # noinspection PyTypeChecker
        app_profile.add_open_files(open_files="", data_retrieval_timestamp=datetime.datetime.now())

    with pytest.raises(TypeError):
        # noinspection PyTypeChecker
        app_profile.add_open_files(open_files=list(), data_retrieval_timestamp=None)


def test_add_open_files() -> None:
    """
    Test add open files for each application.
    """
    processes = psutil.process_iter()
    number_of_processes_checked = 0
    for process in processes:
        if number_of_processes_checked > 0:
            break
        process_name = process.name()
        app_profile = AppProfile(application_name=process_name)
        try:
            timestamp = datetime.datetime.now()
            process_open_files = process.open_files()
            app_profile.add_open_files(open_files=process_open_files, data_retrieval_timestamp=timestamp)
            application_open_files = app_profile.get_open_files()
            assert len(application_open_files) == 1
            application_open_files_batch = application_open_files[0]
            # Some files may be repeated when retrieved from the psutil.
            assert len(process_open_files) >= len(application_open_files_batch), \
                """The length of expected open files is not equal nor larger than actual open files."
                    "\nProcess_open_files: {}\n Application open files: {}""".format(process_open_files,
                                                                                     application_open_files_batch)

            for open_file in process_open_files:
                assert open_file.path in application_open_files_batch
        except AccessDenied:  # Permission error if test is not run as admin.
            continue
        except OSError:
            continue
    print("Number of processes checked: " + str(number_of_processes_checked))


def test_cpu_percent_value_when_adding_process_object_to_application_profile() -> None:
    """
    Test that getting cpu_percent when adding processes to an application profile is not always 0.0.
    """
    processes = psutil.process_iter()
    number_of_ps_with_non_zero_cpu_usage = 0  # Some applications may have 0.0 of cpu usage
    for process in processes:
        app_profile = AppProfile("Some application")
        try:
            app_profile.add_new_information_from_process_object(process=process,
                                                                data_retrieval_timestamp=datetime.datetime.now())
        except (psutil.NoSuchProcess, psutil.ZombieProcess, psutil.AccessDenied):
            continue

        if all(cpu_percentage >= 0.0 for cpu_percentage in app_profile.get_cpu_percentages()):
            number_of_ps_with_non_zero_cpu_usage += 1
    assert number_of_ps_with_non_zero_cpu_usage > 0


def test_dict_format() -> None:
    """
    Test dict_format() for an application profile. It checks that the returned value is in the right format.
    """

    process_handler = ProcessHandler(logger_name, True)
    process_handler.collect_running_processes_information()
    registered_applications = process_handler.get_registered_app_profiles_list()
    for registered_app in registered_applications:
        registered_app_dict = registered_app.dict_format()

        check_app_profile_has_the_right_format(app_name=registered_app.get_application_name(),
                                               app_profile=registered_app_dict)
        # Check that all datetime values are in string format. Will throw an error if it is not in the right format.
        object_created_timestamp = registered_app_dict[AppProfileAttribute.date_created_timestamp.name]
        datetime.datetime.strptime(object_created_timestamp, wades_config.datetime_format)
        retrieval_timestamps = registered_app_dict[AppProfileAttribute.data_retrieval_timestamps.name]
        for retrieval_timestamp in retrieval_timestamps:
            datetime.datetime.strptime(retrieval_timestamp, wades_config.datetime_format)


# noinspection PyTypeChecker
def test_set_app_profile_value_from_dict_input_validation() -> None:
    """
    Test set_value_from_dict() with input validation.
    """
    app_profile = AppProfile("Some name")

    # None type as input
    with pytest.raises(TypeError):
        app_profile.set_value_from_dict(None)

    # String as input
    with pytest.raises(TypeError):
        app_profile.set_value_from_dict("DS")

    # Empty dictionary as input. No required keys are used.
    with pytest.raises(ValueError):
        app_profile.set_value_from_dict(dict())


def test_get_normalized_app_profile_data() -> None:
    """
    Test get_previously_retrieved_data() with sample data.
    It checks that the expected value of the sample app_profile is returned by get_previously_retrieved_data().
    """
    app_name = "common_case_app"
    last_retrieved_timestamp = "2021-01-d 23:33:03:575118"

    app_profiles = AppProfileDataManager.get_saved_profiles_as_dict(SAMPLE_APP_PROF_DATA_PATH)
    app_profile_dict = app_profiles[app_name]

    app_profile = AppProfile(application_name=app_name)
    app_profile.set_value_from_dict(app_profile_dict=app_profile_dict)
    normalized_retrieved_data_size = \
        len(app_profile.get_data_retrieval_timestamps()) - app_profile.get_latest_retrieved_data_size()

    assert normalized_retrieved_data_size == 4

    # Build expected normalized app profile
    expected_normalized_app_profile = {
        AppProfileAttribute.app_name.name: app_name,
        AppProfileAttribute.memory_infos.name:
            app_profile_dict[AppProfileAttribute.memory_infos.name][:normalized_retrieved_data_size],

        AppProfileAttribute.cpu_percents.name:
            app_profile_dict[AppProfileAttribute.cpu_percents.name][:normalized_retrieved_data_size],

        AppProfileAttribute.children_counts.name:
            app_profile_dict[AppProfileAttribute.children_counts.name][:normalized_retrieved_data_size],

        AppProfileAttribute.usernames.name:
            app_profile_dict[AppProfileAttribute.usernames.name][:normalized_retrieved_data_size],

        AppProfileAttribute.opened_files.name:
            app_profile_dict[AppProfileAttribute.opened_files.name][:normalized_retrieved_data_size],

        AppProfileAttribute.data_retrieval_timestamps.name:
            app_profile_dict[AppProfileAttribute.data_retrieval_timestamps.name][:normalized_retrieved_data_size]
    }

    actual_normalized_app_profile = app_profile.get_previously_retrieved_data()

    assert actual_normalized_app_profile == expected_normalized_app_profile


def test_get_latest_retrieved_data() -> None:
    """
    Test get_latest_retrieved_data() with sample data.
    It checks that the expected value of the sample app_profile is returned by get_latest_retrieved_data().
    """
    app_name = "common_case_app"
    last_retrieved_timestamp = "2021-01-d 23:33:03:575118"

    app_profiles = AppProfileDataManager.get_saved_profiles_as_dict(SAMPLE_APP_PROF_DATA_PATH)
    app_profile_dict = app_profiles[app_name]

    app_profile = AppProfile(application_name=app_name)
    app_profile.set_value_from_dict(app_profile_dict=app_profile_dict)
    latest_retrieved_data_size = app_profile.get_latest_retrieved_data_size()
    assert latest_retrieved_data_size == 1

    # Build expected latest app profile data
    expected_latest_app_profile_data = {
        AppProfileAttribute.app_name.name: app_name,
        AppProfileAttribute.memory_infos.name:
            app_profile_dict[AppProfileAttribute.memory_infos.name][-latest_retrieved_data_size:],

        AppProfileAttribute.cpu_percents.name:
            app_profile_dict[AppProfileAttribute.cpu_percents.name][-latest_retrieved_data_size:],

        AppProfileAttribute.children_counts.name:
            app_profile_dict[AppProfileAttribute.children_counts.name][-latest_retrieved_data_size:],

        AppProfileAttribute.usernames.name:
            app_profile_dict[AppProfileAttribute.usernames.name][-latest_retrieved_data_size:],

        AppProfileAttribute.opened_files.name:
            app_profile_dict[AppProfileAttribute.opened_files.name][-latest_retrieved_data_size:],
        AppProfileAttribute.data_retrieval_timestamps.name:
            app_profile_dict[AppProfileAttribute.data_retrieval_timestamps.name][-latest_retrieved_data_size:]
    }
    actual_latest_app_profile_data = app_profile.get_latest_retrieved_data()

    assert actual_latest_app_profile_data == expected_latest_app_profile_data
