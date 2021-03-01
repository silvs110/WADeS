import json
import sys
import socket
from pprint import pprint
from typing import Any

import wades_config
from src.main.WadesDaemon import WadesDaemon
from src.utils.error_messages import expected_type_but_received_message


def send_request(request: str) -> Any:
    """
    Opens a connection the modeller daemon and send a request.
    :param request: The message to send to the modeller.
    :type request: str
    :return: The response from the modeller.
    :rtype: Any
    """
    if not isinstance(request, str):
        raise TypeError(expected_type_but_received_message.format('request', 'str', request))
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client.connect((wades_config.localhost_address, wades_config.modeller_thread_port))
    except ConnectionRefusedError:
        return "Modeller service is not accepting requests. Check configuration file and " \
               "change run_modeller_server value to True."
    client.sendall(request.encode())
    data = b''
    while True:
        response_from_server = client.recv(4096)
        if not response_from_server:
            break

        data += response_from_server

    client.close()
    return json.loads(data)


def print_supported_commands() -> None:
    """
    Prints the list of supported commands.
    """
    supported_commands = ["start", "stop",
                          "modeller pause", "modeller status", "modeller continue", "abnormal apps",
                          "modelled apps", "modelled apps --history", "help"]
    for i in range(1, len(supported_commands) + 1):
        print("{}. {}".format(i, supported_commands[i - 1]))


def main(argv: list) -> None:
    """
    Handles the commands provided.
    :param argv: The command to execute.
    :type argv: list
    """
    arguments = " ".join(argv).strip()
    wades_daemon = WadesDaemon()
    wades_daemon.start()
    if arguments == "start":
        wades_daemon.start()
    elif arguments == "stop":
        wades_daemon.terminate()
    elif arguments in ["modeller pause", "modeller status", "modeller continue"]:
        response = send_request(arguments)
        pprint(response)
    elif arguments in ["abnormal apps", "modelled apps", "abnormal apps --history"]:
        abnormal_apps = send_request(arguments)
        pprint(abnormal_apps)
    elif arguments == "help":
        print_supported_commands()
    else:
        print("Invalid command.")


if __name__ == "__main__":
    main(sys.argv[1:])
