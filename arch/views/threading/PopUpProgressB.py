from PyQt5.QtWidgets import QWidget, QProgressBar, QVBoxLayout


class PopUpProgressB(QWidget):
    def __init__(self):
        super().__init__()
        self.pbar = QProgressBar(self)
        self.pbar.setRange(0, 0)
        self.pbar.setGeometry(30, 40, 500, 75)
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.pbar)

        self.setLayout(self.layout)
        self.setGeometry(300, 300, 550, 100)
        self.setWindowTitle('Trying to find more solutions')

    def stop(self):
        self.deleteLater()
