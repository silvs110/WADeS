from enum import Enum


class AppProfileAttribute(Enum):
    # Enums are similar to ProcessAttribute enums, but have different name conventions.
    # MAY change this in future iterations.
    app_name = 1
    date_created_timestamp = 2
    usernames = 3
    memory_infos = 4
    opened_files = 5
    cpu_percents = 6
    children_counts = 7
    threads_numbers = 8
    connections_numbers = 9
    data_retrieval_timestamps = 10


