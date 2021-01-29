from enum import Enum


class ProcessAttribute(Enum):
    # Enums from 1 to 6 have the same name as the attributes in psutil.Process
    name = 1
    pid = 2
    username = 3
    memory_info = 4
    open_files = 5
    cpu_percent = 6
    children_count = 7
