from PyQt5.QtWidgets import QTreeWidget, QWidget, QListWidget
from PyQt5.uic.properties import QtWidgets


class ApplicationList(QListWidget):
    def __init__(self, parent: QWidget = None) -> None:
        super(QListWidget, self).__init__(parent)
        self.setWindowTitle("Application Lists")
        size = self.size()
        self.setFixedSize(size)