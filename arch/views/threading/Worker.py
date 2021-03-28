from PyQt5.QtCore import QRunnable, QObject, pyqtSignal


class Worker(QRunnable):
    def __init__(self, it, prog):
        super(Worker, self).__init__()
        self.it = it
        self.signals = WorkerSignals()
        prog.show()

    def run(self) -> None:
        try:
            model = next(self.it)
            self.signals.finished.emit(model)
        except StopIteration:
            self.signals.error.emit()
        except KeyboardInterrupt:
            return None


class WorkerSignals(QObject):
    finished = pyqtSignal(object)
    error = pyqtSignal()
