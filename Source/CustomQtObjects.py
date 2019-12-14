from PyQt5.QtWidgets import QGraphicsDropShadowEffect, QLineEdit, QTreeView, QWidget, QVBoxLayout, QGroupBox, QAbstractItemView, QGridLayout, QPushButton
from PyQt5.QtCore import QDate, QDateTime, QRegExp, QSortFilterProxyModel, Qt, QTime, QModelIndex, QSize, pyqtSignal, QObject
from PyQt5.QtGui import QStandardItemModel, QIcon, QStandardItem

class Button(QPushButton):
    def __init__(self, name=None):
        super(Button, self).__init__()
        self.setMouseTracking(True)
        self.setText(name)
        
    def enterEvent(self, event):
        if self.isEnabled():
            shadow = QGraphicsDropShadowEffect()
            shadow.setBlurRadius(2)
            shadow.setOffset(3, 3)
            self.setGraphicsEffect(shadow)

    def leaveEvent(self, event):
        self.setGraphicsEffect(None)

class LineEdit(QLineEdit):
    def __init__(self, name=None):
        super(LineEdit, self).__init__()
        self.setText(name)
        
    def focusInEvent(self, event):
        QLineEdit.focusInEvent(self, event)
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(2)
        shadow.setOffset(3, 3)
        self.setGraphicsEffect(shadow)

    def focusOutEvent(self, event):
        QLineEdit.focusOutEvent(self, event)
        self.setGraphicsEffect(None)

class DeselectableTreeView(QTreeView):
    def mousePressEvent(self, e):
        self.clearSelection()
        QTreeView.mousePressEvent(self, e)

    def focusOutEvent(self, event):
        QTreeView.focusOutEvent(self, event)
        self.clearSelection()

class Table(QWidget):
    def __init__(self, name, data, columns=None, index=False, checkable=False, parent=None):
        QWidget.__init__(self, parent)

        self.name = name
        self.index = index
        self.checkable = checkable            
        
        if not any([data, columns]):
            self.columns = []
        else:
            self.columns = columns if columns else list(data[0].keys())
        
        if checkable:
            self.columns.insert(0, '')

        if index:
            self.columns.insert(0, 'ID')
        
        self.setData(data)

        self.initUI()

    def initUI(self):
     #  Layout UI elements of table
        
        mainLayout = QVBoxLayout()

        self.proxyModel = QSortFilterProxyModel()
        self.proxyModel.setDynamicSortFilter(True)

        self.sourceModel = QStandardItemModel(0, len(self.columns), self)
        
        for i, column in enumerate(self.columns):
            self.sourceModel.setHeaderData(i, Qt.Horizontal, column)

        self.proxyModel.setSourceModel(self.sourceModel)
        
        self.proxyGroupBox = QGroupBox(self.name)

        self.proxyView = DeselectableTreeView()
        self.proxyView.setRootIsDecorated(False)
        self.proxyView.setAlternatingRowColors(True)
        self.proxyView.setModel(self.proxyModel)

        if not self.checkable:
            self.proxyView.setSortingEnabled(True)
            self.proxyView.sortByColumn(0, Qt.AscendingOrder)

        self.proxyView.setEditTriggers(QAbstractItemView.NoEditTriggers)

        proxyLayout = QGridLayout()
        proxyLayout.addWidget(self.proxyView, 0, 0, 1, 3)
        self.proxyGroupBox.setLayout(proxyLayout)

        mainLayout.addWidget(self.proxyGroupBox)
        self.setLayout(mainLayout)
        self.update(self.data)  
    
    def setSourceModel(self, model):
        self.proxyModel.setSourceModel(model)

    def setData(self, data):
        self.data = []
        for i, item in enumerate(data):
            d = {}
            for col in self.columns:
                if col == 'ID':
                    d[col] = item.get(col, i+1)
                else:
                    d[col] = item.get(col)
            self.data.append(d)

        #self.data = [{k: item.get(k, i+1) for k in self.columns} for i, item in enumerate(data)]

    def sortBy(self, colName):
        idx = 0
        try:
            idx = self.columns.index(colName)
        except:
            pass

        self.proxyView.sortByColumn(idx, Qt.AscendingOrder)

    def rowCount(self):
        return self.sourceModel.rowCount()

    def columnCount(self):
        return self.sourceModel.columnCount()

    def addRow(self, row_i, rowData):
        self.sourceModel.insertRow(row_i)

        for col_i, data in enumerate(rowData.values()):
            if self.checkable and col_i == 0:
                self.proxyView.setColumnWidth(col_i, 1)
                item = QStandardItem(True)
                item.setCheckable(True)
                item.setCheckState(False)
                self.sourceModel.setItem(row_i, col_i, item)
            else:
                self.sourceModel.setData(self.sourceModel.index(row_i, col_i), data)
            
    def update(self, data):
        self.setData(data)
        self.sourceModel.removeRows(0, self.sourceModel.rowCount())
        
        for i, data in enumerate(self.data):
            self.addRow(i, data)

    def getSelectedRowIndex(self):
        '''
        Returns the index of the selected row from the source model
        '''
        try:
            return self.proxyModel.mapToSource(self.proxyView.selectedIndexes()[0]).row()
        except:
            return False

    def getCheckedRowData(self):
        selectedData = []
        for row_i in range(self.sourceModel.rowCount()):
            item = self.sourceModel.item(row_i, 0)
            if item.checkState():
                selectedData.append(self.data[row_i])

        return selectedData
