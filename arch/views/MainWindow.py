import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QAction
from arch.views.MainWidget import MainWidget

from typing import Callable


class MainWindow(QApplication):
    def __init__(self, file):
        super().__init__(sys.argv)
        self.width = self.primaryScreen().availableGeometry().width()
        self.height = self.primaryScreen().availableGeometry().height()
        self.window = Window(self.width, self.height, file)


class Window(QMainWindow):
    def __init__(self, width: int, height: int, file):
        super().__init__()
        self.width = width
        self.height = height
        self.widget = MainWidget(self, width, height)

        self.add_action("Open", "Ctrl-O", self.widget.open)
        self.add_action("Generate", "Ctrl-G", self.widget.generate)
        self.add_action("Next", "Ctrl-N", self.widget.next)
        self.add_action("Solve", "Ctrl-N", self.widget.solve)
        act = self.add_action("Prev", "Ctrl-P", self.widget.prev)

        self.height = self.toolbar.actionGeometry(act).height()
        self.show()
        if file:
            self.widget.open(file)

    def add_action(self, name: str, shortcut: str,
                   action: Callable) -> QAction:
        act = QAction(name, self)
        act.setShortcut(shortcut)
        act.triggered.connect(action)
        self.toolbar = self.addToolBar(name)
        self.toolbar.addAction(act)
        return act
