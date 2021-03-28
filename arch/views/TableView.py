from PyQt5.QtCore import QAbstractTableModel, Qt
from PyQt5.QtWidgets import QWidget, QTableView, QHeaderView

CELL_SIZE = 40
FONT_SIZE = 30


class TableModel(QAbstractTableModel):
    def __init__(self, data):
        super(TableModel, self).__init__()
        self._data = data

    def data(self, index: int, role: int):
        if role == Qt.DisplayRole:
            return self._data[index.row()][index.column()]

    def rowCount(self, index: int):
        return len(self._data)

    def columnCount(self, index: int):
        return len(self._data[0])


class TableView(QTableView):
    def __init__(self, parent: QWidget, width: int, height: int):
        super().__init__(parent)

        self.horizontalHeader().setDefaultSectionSize(CELL_SIZE)
        self.verticalHeader().setDefaultSectionSize(CELL_SIZE)
        self.verticalHeader().setSectionResizeMode(QHeaderView.Fixed)
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Fixed)
        self.verticalHeader().hide()
        self.horizontalHeader().hide()
        self.verticalScrollBar().setDisabled(False)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.horizontalScrollBar().setDisabled(False)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        fnt = self.font()
        fnt.setPixelSize(FONT_SIZE)
        self.setFont(fnt)

        self.setGeometry(0, 0, width, height)
