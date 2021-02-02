from src.main.modeller.Modeller import Modeller
from src.main.psHandler.ProcessHandler import ProcessHandler

if __name__ == "__main__":
    ps_handler = ProcessHandler()
    modeller = Modeller()
    ps_handler.terminate()
    modeller.terminate()
