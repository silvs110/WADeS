from pprint import pprint
from time import sleep

import psutil


def run_data_collector() -> None:
    """

    :return:
    """

    while(True):
        running_pids = psutil.pids()
        for running_pid in running_pids:
            process = psutil.Process(running_pid)
            pprint(process)

        sleep(100)

run_data_collector()