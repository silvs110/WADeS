import threading
from time import sleep

from src.main.modeller.Modeller import Modeller
from src.main.psHandler.ProcessHandler import ProcessHandler

if __name__ == "__main__":

    modeller = Modeller()
    ps_handler = ProcessHandler()
    exit_program = False
    while not exit_program:
        user_input = str(input("command: "))

        if user_input == "modeller start":
            modeller.start()
        elif user_input == "pshandler start":
            ps_handler.start()
        elif user_input == "pshandler terminate":
            ps_handler.terminate()
        elif user_input == "modeller terminate":
            modeller.terminate()
        elif user_input == "exit":
            exit_program = True
        else:
            continue
