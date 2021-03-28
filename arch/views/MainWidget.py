from typing import List

from PyQt5.QtCore import QThreadPool
from PyQt5.QtWidgets import QWidget, QMainWindow, QFileDialog, QMessageBox, \
    QInputDialog

from arch.fillomino import Fillomino, file_reader, get_from_string
from arch.fillomino_solver import FillominoSolver
from arch.generator import Generator
from arch.views.TableView import TableModel, TableView, CELL_SIZE
from arch.views.threading.Worker import Worker
from arch.views.threading.PopUpProgressB import PopUpProgressB


def clear_data(arr):
    for i in range(len(arr)):
        for j in range(len(arr[i])):
            if not arr[i][j].isdigit():
                arr[i][j] = ''
    return arr


class MainWidget(QWidget):
    def __init__(self, parent: QMainWindow, width, height):
        super().__init__(parent)
        self.container = parent
        self.w = width
        self.h = height
        self.setWindowTitle('Fillomino Solver')
        self.data = None
        self.model = None
        self.view = None
        self.in_progress = False
        self.prog = None
        self.puzzle = None
        self.solver = None
        self.threadpool = QThreadPool()
        self.it = None
        self.models = []
        self.index = 0

    def set_data(self, data: List[List[int]]):
        self.data = data
        self.update_view()

    def update_view(self) -> None:
        self.model = TableModel(self.data)
        if self.view:
            self.view.deleteLater()
        self.view = TableView(self,
                              min(CELL_SIZE * len(self.data[0]), self.w - 50),
                              min(CELL_SIZE * len(self.data), self.h - 70))
        self.setGeometry(25, self.container.height,
                         self.w,
                         self.h)
        self.container.setGeometry(0, 0,
                                   self.w,
                                   self.h)
        self.view.setModel(self.model)
        self.view.show()

    def open(self, file_name=None) -> None:
        if not file_name:
            self.models = []
            options = QFileDialog.Options()
            options |= QFileDialog.DontUseNativeDialog
            title = "Choose File"
            directory = ""
            files = "Txt Files (*.txt);;All Files (*)"
            file_name, _ = QFileDialog.getOpenFileName(self,
                                                       title,
                                                       directory,
                                                       files,
                                                       options=options)
        if file_name:
            self.open_file(file_name)

    def next(self) -> None:
        if self.index == len(self.models) - 1:
            if not self.in_progress:
                self.prog = PopUpProgressB()
                worker = Worker(self.it, self.prog)
                worker.signals.finished.connect(self.set_model)
                worker.signals.error.connect(self.error_dialog)
                self.in_progress = True
                self.threadpool.start(worker)
        else:
            self.index += 1
            if self.index < len(self.models):
                self.set_data(self.models[self.index])
            else:
                self.index -= 1

    def set_model(self, model):
        self.models.append(model.as_array())
        self.set_data(model.as_array())
        self.index += 1
        self.in_progress = False
        self.prog.stop()

    def error_dialog(self):
        msg = QMessageBox()
        msg.setText("No more solutions")
        msg.setWindowTitle("Error")
        msg.exec_()
        self.in_progress = False
        self.prog.stop()

    def prev(self) -> None:
        if self.index > 0:
            self.index -= 1
            if self.models[self.index]:
                self.set_data(self.models[self.index])

    def generate(self) -> None:
        self.models = []
        rows, res1 = QInputDialog.getInt(self, "Rows number",
                                         "Write number of rows")
        if res1:
            cols, res2 = QInputDialog.getInt(self, "Cols number",
                                             "Write number of cols")
            if res2:
                if rows == 0 or cols == 0:
                    msg = QMessageBox()
                    msg.setText("Incorrect input!")
                    msg.setWindowTitle("Error")
                    msg.exec_()
                else:
                    gen = Generator(rows, cols, (1, 9))
                    self.puzzle = Fillomino(rows, cols, gen.puzzle)
                    data = clear_data(self.puzzle.as_array())
                    self.set_data(data)

    def solve(self) -> None:
        self.init_solver()

    def init_solver(self):
        self.solver = FillominoSolver(self.puzzle)
        self.solver.solve()
        self.it = self.solver.get_next_model()
        try:
            model = next(self.it).as_array()
            self.models.append(model)
            self.set_data(model)
        except StopIteration:
            msg = QMessageBox()
            msg.setText("No solutions!")
            msg.setWindowTitle("Error")
            msg.exec_()

    def open_file(self, file):
        self.puzzle = Fillomino(*get_from_string(file, file_reader),
                                True)
        if self.puzzle.err:
            msg = QMessageBox()
            msg.setText("Incorrect input!")
            msg.setWindowTitle("Error")
            msg.exec_()
        else:
            self.data = self.puzzle.as_array()
            self.data = clear_data(self.data)

            self.set_data(self.data)
