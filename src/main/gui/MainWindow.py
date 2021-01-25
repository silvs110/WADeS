import sys

from PyQt5.QtWidgets import QMainWindow, QApplication

from src.main.gui.ApplicationList import ApplicationList


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setWindowTitle("WADeS")
        self.setFixedSize(500, 500)
        self.application_lists = ApplicationList(self)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec_())
