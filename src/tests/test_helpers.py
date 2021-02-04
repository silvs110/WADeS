from typing import Dict, Set, List

from src.main.common.AppProfile import AppProfile
from src.main.common.enum.AppProfileAttribute import AppProfileAttribute


def build_application_profile_list(app_profiles_dict: Dict[str, dict], application_names: Set[str] = None) \
        -> List[AppProfile]:
    """
    Helper method for converting application profiles as dict forms to ApplicationProfile objects.
    :param app_profiles_dict: All application profiles.
        Format:
            {
                "Some name": {
                    app_name: "Some name",
                    date_created_timestamp: "2020-12-12 14:30:32:34.232",
                    usernames: [user_1, user_2, ...]
                    memory_infos: [2342, 23215, 31573, ...],
                    opened_files:
                        {
                            timestamp_1 : {
                                path_1: [permission_1, permission_2, ...],
                                ...
                            },
                            ...
                        },
                    cpu_percents: [0.2, 13.9, ...],
                    children_counts: [1, 5, 0, 4, ...]
                    data_retrieval_timestamps: [timestamp_1, timestamp_2, ...],
                    threads_numbers:[0, 1, 3, 9, ...],
                    connections_numbers:[0, 1, 3, 9, ...]
                },
                ...
            }
    :type app_profiles_dict: Dict[str, dict]
    :param application_names: The name of the application profiles to convert to AppProfile objects.
    :type application_names: Set[str]
    :return: A list of application profiles.
    :rtype: List[AppProfile]
    """
    app_profiles = list()
    app_names_to_use = application_names if application_names is not None else app_profiles_dict.keys()
    for application_name in app_names_to_use:
        app_profile = AppProfile(application_name=application_name)
        app_profile.set_value_from_dict(app_profiles_dict[application_name])
        app_profiles.append(app_profile)
    return app_profiles


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
