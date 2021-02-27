from typing import Dict, Set, List, Any

from src.main.common.AppProfile import AppProfile
from src.main.common.enum.AppProfileAttribute import AppProfileAttribute


# noinspection DuplicatedCode
def check_app_profile_has_the_right_format(app_name: str, app_profile: dict) -> None:
    """
    Helper method that checks that the app_profile dictionary is in the right format.
    For more info of the expected format:
        src.main.common.AppProfile.AppProfile.dict_format()
    :param app_name: The name of the application.
    :type app_name: str
    :param app_profile: The app_profile to check.
    :type app_profile: dict
    """
    app_profile_name = app_profile[AppProfileAttribute.app_name.name]
    assert app_name == app_profile_name

    app_profile_creation_timestamp = app_profile[AppProfileAttribute.date_created_timestamp.name]
    assert isinstance(app_profile_creation_timestamp, str)

    app_profile_retrieval_times = app_profile[AppProfileAttribute.data_retrieval_timestamps.name]
    assert all(isinstance(timestamp, str) for timestamp in app_profile_retrieval_times)

    memory_usages = app_profile[AppProfileAttribute.memory_infos.name]
    assert all(isinstance(rss_mem, int) for rss_mem in memory_usages)

    cpu_percents = app_profile[AppProfileAttribute.cpu_percents.name]
    assert all(isinstance(cpu_percent, float) for cpu_percent in cpu_percents)

    child_process_counts = app_profile[AppProfileAttribute.children_counts.name]
    assert all(isinstance(children_count, int) for children_count in child_process_counts)

    users = app_profile[AppProfileAttribute.usernames.name]
    assert all(isinstance(user, str) for user in users)

    threads_numbers = app_profile[AppProfileAttribute.threads_numbers.name]
    assert all(isinstance(threads_number, int) for threads_number in threads_numbers)

    connections_numbers = app_profile[AppProfileAttribute.connections_numbers.name]
    assert all(isinstance(connections_number, int) for connections_number in connections_numbers)

    opened_files = app_profile[AppProfileAttribute.opened_files.name]
    assert isinstance(opened_files, list)
    assert all(isinstance(files, (list, set)) and isinstance(file, str) for files in
               opened_files for file in files)
