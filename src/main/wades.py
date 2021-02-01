import json
import socket
from pprint import pprint
from typing import Any

from src.main.modeller.Modeller import Modeller
from src.main.psHandler.ProcessHandler import ProcessHandler
from src.utils.error_messages import expected_type_but_received_message
from wades_config import localhost_address, modeller_thread_port


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
    client.connect((localhost_address, modeller_thread_port))
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
    supported_commands = ["modeller start", "modeller terminate", "pshandler start", "pshandler terminate",
                          "modeller pause", "modeller status", "modeller continue", "abnormal apps", "modelled apps",
                          "exit", "help"]
    for i in range(1, len(supported_commands) + 1):
        print("{}. {}".format(i, supported_commands[i - 1]))


if __name__ == "__main__":

    modeller = Modeller()
    ps_handler = ProcessHandler()
    exit_program = False
    print("Type help for a list of supported commands.")
    while not exit_program:
        user_command = str(input("Command: "))
        # noinspection PyBroadException
        try:
            if user_command == "modeller start":
                modeller.start()
            elif user_command == "pshandler start":
                ps_handler.start()
            elif user_command == "pshandler terminate":
                ps_handler.terminate()
            elif user_command == "modeller terminate":
                modeller.terminate()
            elif user_command in ["modeller pause", "modeller status", "modeller continue"]:
                response = send_request(user_command)
                print(response[0])
            elif user_command in ["abnormal apps", "modelled apps", "abnormal apps --history"]:
                abnormal_apps = send_request(user_command)
                pprint(abnormal_apps)
            elif user_command == "help":
                print_supported_commands()
            elif user_command == "exit":
                exit_program = True
            else:
                print("Command not supported. Try again")
                continue
        except Exception:
            pass
