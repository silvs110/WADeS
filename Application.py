import datetime

import psutil


class Application:

    def __init__(self, process_information: psutil.Process) -> None:
        self.object_creation_timestamp = datetime.datetime.now()
        self.name = process_information.name()
        self.cpu_memory_usages = list()
        self.open_files = list()
        self.io_activities = list()
        self.data_timestamp_retrieval = list()
        self.add_new_information(process_information=process_information, data_retrieval_timestamp=self.object_creation_timestamp)


    def __str__(self) -> str:
        return f"Application: {self.name}"

    def __eq__(self, other: "Application") -> bool:
        return self.name == other.name

    def __ne__(self, other: "Application") -> bool:
        return self.name != other.name

    def add_new_information(self, process_information: psutil.Process, data_retrieval_timestamp: datetime.datetime) -> None:
        self.cpu_memory_usages.append(process_information.cpu_percent())
        self.open_files.append(process_information.open_files())
        self.io_activities.append(process_information.io_counters())
        self.data_timestamp_retrieval.append(data_retrieval_timestamp)


    """
    Stuff to collect:
    - cpu memory usage
    - open files
    - io activity
    - network connections
    - memory usage
    """
