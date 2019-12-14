import os
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QDoubleValidator, QRegExpValidator
from PyQt5.QtCore import Qt, QRegExp, QDateTime
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import Qt, QUrl, pyqtSlot, qInstallMessageHandler
from PyQt5.QtWebChannel import QWebChannel
from statistics import mean
import webbrowser
from functools import partial
from geopy import Point

from MouseController import MouseController
from CustomQtObjects import Button, LineEdit, Table

#Class to confirm the scale input data
class ScaleWindow(QDialog):
    def __init__(self, dist_px, parent=None):
        super(ScaleWindow, self).__init__(parent)

        self.dist_px = dist_px
        self.scale = 1

        self.setWindowTitle('Scale')
        self.initUI()

    def initUI(self):
        '''
        Setup GUI elements of scale window
        '''
        mainLayout = QVBoxLayout()

        #horizontal layout containing lineedits, unit selector, and label
        hLayout = QHBoxLayout() 
        self.pixelEdit = LineEdit(str(self.dist_px))
        self.pixelEdit.setValidator(QDoubleValidator(0.99, 1000.00, 2))
        self.pixelEdit.textChanged.connect(self.checkFields)
        self.scaleEdit = LineEdit(str(self.scale))
        self.scaleEdit.setValidator(QDoubleValidator(0.99, 1000.00, 2))
        self.scaleEdit.textChanged.connect(self.checkFields)

        label = QLabel('Pixels:')

        units = ['km', 'm', 'ft', 'mi']
        self.comboBox = QComboBox()
        self.comboBox.addItems(units)

        hLayout.addWidget(label)
        hLayout.addWidget(self.pixelEdit)
        hLayout.addWidget(self.scaleEdit)
        hLayout.addWidget(self.comboBox)

        #horizontal layout containing save and cancel buttons
        h2Layout = QHBoxLayout()
        self.saveButton = Button('Save')
        self.saveButton.clicked.connect(self.save)

        self.cancelButton = Button('Cancel')
        self.cancelButton.clicked.connect(self.cancel)

        h2Layout.addWidget(self.saveButton)
        h2Layout.addWidget(self.cancelButton)

        mainLayout.addLayout(hLayout)
        mainLayout.addLayout(h2Layout)
    
        self.setLayout(mainLayout)
        self.setModal(True)
        self.show()

    def checkFields(self):
        '''
        Check if all mandatory fields are entered
        '''
        if self.pixelEdit.text() and self.scaleEdit.text():
            self.saveButton.setEnabled(True)
        else:
            self.saveButton.setEnabled(False)

    def getConfirmedData(self):
        return self.pxPerUnit, self.units

    def save(self):
        '''
        Send scale and unit values entered by user back to mouse tracker
        screen when save button is clicked.
        '''
        #Get text values from each element
        self.scale = eval(self.scaleEdit.text())
        self.dist_px = eval(self.pixelEdit.text())
        self.units = self.comboBox.currentText()

        self.pxPerUnit = self.dist_px / self.scale
        
        #check values entered by user are correct
        if self.scale > 0 and self.dist_px > 0:
            self.accept() 
            self.close()

    def cancel(self):
        '''
        Return to mouse tracker screen if cancel button is clicked
        '''
        self.reject()
        self.close()
        
#Class to confirm the reference point data
class ReferenceWindow(QDialog):
    def __init__(self, parent=None):
        super(ReferenceWindow, self).__init__(parent)
        self.resize(400, 100)
        self.setWindowTitle('Add Reference Point')
        self.initUI()

    def initUI(self):
        '''
        Setup GUI elements of scale window
        '''
        mainLayout = QVBoxLayout()

        #horizontal layout containing lineedits, unit selector, and label
        hLayout = QHBoxLayout() 

        self.latEdit = LineEdit()
        self.latEdit.setPlaceholderText('Latitude')
        self.latEdit.textChanged.connect(self.checkFields)

        self.lonEdit = LineEdit()
        self.lonEdit.setPlaceholderText('Longitude')
        self.lonEdit.textChanged.connect(self.checkFields)

        hLayout.addWidget(self.latEdit)
        hLayout.addWidget(self.lonEdit)

        #horizontal layout containing save and cancel buttons
        h2Layout = QHBoxLayout()
        self.saveButton = Button('Save')
        self.saveButton.clicked.connect(self.save)
        self.saveButton.setEnabled(False)

        self.cancelButton = Button('Cancel')
        self.cancelButton.clicked.connect(self.cancel)

        h2Layout.addWidget(self.saveButton)
        h2Layout.addWidget(self.cancelButton)

        mainLayout.addLayout(hLayout)
        mainLayout.addLayout(h2Layout)
    
        self.setLayout(mainLayout)
        self.setModal(True)
        self.show()

    def checkFields(self):
        '''
        Check if all mandatory fields are entered
        '''
        lat = self.latEdit.text()
        lon = self.lonEdit.text()

        if lat and lon:
            self.saveButton.setEnabled(True)
        else:
            self.saveButton.setEnabled(False)

    def getConfirmedData(self):
        return self.lat, self.lon

    def save(self):
        '''
        Send reference point back to main window to be stored
        '''
        lat = self.latEdit.text()
        lon = self.lonEdit.text()

        try:
            point = Point(lat + ' ' + lon)
        except:
            QMessageBox.information(
                self,
                'Reference Point Error',
                f'Invalid reference point: ({lat}, {lon})'
            )
        else:
            self.lat = round(point.latitude, 6)
            self.lon = round(point.longitude, 6)
            self.accept()
            self.close()
            

    def cancel(self):
        '''
        Return to mouse tracker screen if cancel button is clicked
        '''
        self.reject()
        self.close()

#Class to confirm the reference point data
class AddPointWindow(QDialog):
    def __init__(self, parent=None):
        super(AddPointWindow, self).__init__(parent)
        self.resize(400, 100)
        self.setWindowTitle('Add Map Point')
        self.initUI()

    def initUI(self):
        '''
        Setup GUI elements of scale window
        '''
        mainLayout = QVBoxLayout()

        #horizontal layout containing lineedits, unit selector, and label
        hLayout = QHBoxLayout() 

        self.latEdit = LineEdit()
        self.latEdit.setPlaceholderText('Latitude')
        self.latEdit.textChanged.connect(self.checkFields)

        self.lonEdit = LineEdit()
        self.lonEdit.setPlaceholderText('Longitude')
        self.lonEdit.textChanged.connect(self.checkFields)

        hLayout.addWidget(self.latEdit)
        hLayout.addWidget(self.lonEdit)

        #horizontal layout to hold description box
        h2Layout = QHBoxLayout()
        self.descBox = QTextEdit()
        self.descBox.setFixedHeight(100)
        self.descBox.setPlaceholderText('Description')
        h2Layout.addWidget(self.descBox)

        #horizontal layout containing save and cancel buttons
        h3Layout = QHBoxLayout()
        self.saveButton = Button('Save')
        self.saveButton.clicked.connect(self.save)
        self.saveButton.setEnabled(False)

        self.cancelButton = Button('Cancel')
        self.cancelButton.clicked.connect(self.cancel)

        h3Layout.addWidget(self.saveButton)
        h3Layout.addWidget(self.cancelButton)

        mainLayout.addLayout(hLayout)
        mainLayout.addLayout(h2Layout)
        mainLayout.addLayout(h3Layout)
    
        self.setLayout(mainLayout)
        self.setModal(True)
        self.show()

    def checkFields(self):
        '''
        Check if all mandatory fields are entered
        '''
        if self.lonEdit.text() and self.latEdit.text():
            self.saveButton.setEnabled(True)
        else:
            self.saveButton.setEnabled(False)

    def getConfirmedData(self):
        return {
            'Latitude': self.lat,
            'Longitude': self.lon,
            'Date': QDateTime().currentDateTime().toString('MM-dd-yyyy hh:mm:ss ap'),
            'Description': self.desc
        }

    def save(self):
        '''
        Send reference point back to main window to be stored
        '''
        #Get text values from each element
        lat = self.latEdit.text()
        lon = self.lonEdit.text()
        self.desc = self.descBox.toPlainText()

        lat = self.latEdit.text()
        lon = self.lonEdit.text()

        try:
            point = Point(lat + ' ' + lon)
        except:
            QMessageBox.information(
                self,
                'Point Location Error',
                f'Invalid location: ({lat}, {lon})'
            )
        else:
            self.lat = round(point.latitude, 6)
            self.lon = round(point.longitude, 6)
            self.accept()
            self.close()

    def cancel(self):
        '''
        Return to mouse tracker screen if cancel button is clicked
        '''
        self.reject()
        self.close()
        
#Class to confirm lat, lon data
class LocationWindow(QDialog):
    def __init__(self, lat, lon, parent=None):
        super(LocationWindow, self).__init__(parent)
        self.lat = lat
        self.lon = lon

        #self.setFixedSize(300, 100)
        self.setWindowTitle('Confirm Location')
        self.setAttribute(Qt.WA_QuitOnClose, False)
        self.initUI()

    def initUI(self):
        '''
        Setup GUI elements of scale window
        '''
        mainLayout = QVBoxLayout()

        #horizontal layout containing lineedits, unit selector, and label
        hLayout = QHBoxLayout() 
        self.latEdit = LineEdit(str(self.lat))
        self.latEdit.textChanged.connect(self.checkFields)
        hLayout.addWidget(self.latEdit)

        self.lonEdit = LineEdit(str(self.lon))
        self.lonEdit.textChanged.connect(self.checkFields)
        hLayout.addWidget(self.lonEdit)

        self.descBox = QTextEdit()
        self.descBox.setFixedHeight(100)
        self.descBox.setPlaceholderText('Description')

        #horizontal layout containing save and cancel buttons
        h2Layout = QHBoxLayout()
        self.saveButton = Button('Save')
        self.saveButton.clicked.connect(self.save)

        self.cancelButton = Button('Cancel')
        self.cancelButton.clicked.connect(self.cancel)

        h2Layout.addWidget(self.saveButton)
        h2Layout.addWidget(self.cancelButton)

        mainLayout.addLayout(hLayout)
        mainLayout.addWidget(self.descBox)
        mainLayout.addLayout(h2Layout)
    
        self.setLayout(mainLayout)
        self.setModal(True)
        self.show()

    def checkFields(self):
        '''
        Check if all mandatory fields are entered
        '''
        if self.latEdit.text() and self.lonEdit.text():
            self.saveButton.setEnabled(True)
        else:
            self.saveButton.setEnabled(False)

    def getConfirmedData(self):
        return {
            'Latitude': self.lat,
            'Longitude': self.lon,
            'Date': QDateTime().currentDateTime().toString('MM-dd-yyyy hh:mm:ss ap'),
            'Description': self.desc
        }

    def save(self):
        '''
        Send scale and unit values entered by user back to mouse mainwindow
        screen when save button is clicked.
        '''
        lat = self.latEdit.text()
        lon = self.lonEdit.text()
        self.desc = self.descBox.toPlainText()

        lat = self.latEdit.text()
        lon = self.lonEdit.text()

        try:
            point = Point(lat + ' ' + lon)
        except:
            QMessageBox.information(
                self,
                'Point Location Error',
                f'Invalid location: ({lat}, {lon})'
            )
        else:
            self.lat = round(point.latitude, 6)
            self.lon = round(point.longitude, 6)
            self.accept()
            self.close()

    def cancel(self):
        '''
        Return to mouse tracker screen if cancel button is clicked
        '''
        self.reject()
        self.close()

class MouseSettingsWindow(QDialog):
    def __init__(self, parent=None):
        super(MouseSettingsWindow, self).__init__(parent)

        self.mc = MouseController()

        #store original settings
        self.origSpeed = self.mc.getSpeed()
        self.origAccel = self.mc.getAcceleration()

        #create variables for updated settings
        self.speedSetting = self.origSpeed
        self.accelSetting = self.origAccel

        self.setWindowTitle('Mouse Settings')
        self.setAttribute(Qt.WA_QuitOnClose, False)
        self.initUI()

    def initUI(self):
        '''
        Setup GUI elements of scale window
        '''
        mainLayout = QVBoxLayout()

        #horizontal layout containing lineedits, unit selector, and label
        hLayout = QHBoxLayout()
        sliderLabel = QLabel('Sensitivity:')

        self.sl = QSlider(Qt.Horizontal)
        self.sl.setMinimum(1)
        self.sl.setMaximum(20)
        self.sl.setValue(self.origSpeed)
        self.sl.setTickPosition(QSlider.TicksBelow)
        self.sl.setTickInterval(5)
        self.sl.valueChanged.connect(lambda: self.mc.setSpeed(self.sl.value()))

        self.checkBox = QCheckBox('Acceleration')
        self.checkBox.setChecked(self.origAccel)
        self.checkBox.stateChanged.connect(lambda: self.mc.setAcceleration(self.checkBox.isChecked()))

        hLayout.addWidget(sliderLabel)
        hLayout.addWidget(self.sl)

        #horizontal layout containing save and cancel buttons
        h2Layout = QHBoxLayout()
        self.saveButton = Button('Save')
        self.saveButton.clicked.connect(self.save)

        self.cancelButton = Button('Cancel')
        self.cancelButton.clicked.connect(self.cancel)

        h2Layout.addWidget(self.saveButton)
        h2Layout.addWidget(self.cancelButton)

        mainLayout.addLayout(hLayout)
        mainLayout.addWidget(self.checkBox)
        mainLayout.addLayout(h2Layout)
    
        self.setLayout(mainLayout)
        self.setModal(True)
        self.show()

    def save(self):
        '''
        Exit window with updated mouse settings
        '''
        self.close()

    def cancel(self):
        '''
        Set mouse and acceleration back to original settings and close window
        '''
        self.mc.setSpeed(self.origSpeed)
        self.mc.setAcceleration(self.origAccel)
        self.close()

class APIKeyWindow(QDialog):
    def __init__(self, parent=None):
        super(APIKeyWindow, self).__init__(parent)        
        self.setWindowTitle('Enter API Key')
        self.setAttribute(Qt.WA_QuitOnClose, False)
        self.setModal(True)
        self.resize(400, 150)
        self.initUI()

    def initUI(self):
        '''
        Setup GUI elements of scale window
        '''
        mainLayout = QVBoxLayout()

        hLayout = QHBoxLayout()
        self.apiKeyEdit = LineEdit()
        self.apiKeyEdit.setPlaceholderText('Google API Key')
        self.apiKeyEdit.textChanged.connect(self.checkFields)

        self.helpButton = Button('?')
        self.helpButton.setMaximumWidth(25)
        self.helpButton.clicked.connect(lambda: webbrowser.open('https://developers.google.com/maps/documentation/javascript/get-api-key'))

        hLayout.addWidget(self.apiKeyEdit)
        hLayout.addWidget(self.helpButton)

        #horizontal layout containing save and cancel buttons
        h2Layout = QHBoxLayout()
        self.saveButton = Button('Save')
        self.saveButton.clicked.connect(self.save)

        self.cancelButton = Button('Cancel')
        self.cancelButton.clicked.connect(self.cancel)

        h2Layout.addWidget(self.saveButton)
        h2Layout.addWidget(self.cancelButton)

        mainLayout.addLayout(hLayout)
        mainLayout.addLayout(h2Layout)
    
        self.setLayout(mainLayout)
        self.setModal(True)
        self.show()

    def checkFields(self):
        '''
        Check if all mandatory fields are entered
        '''
        if self.apiKeyEdit.text():
            self.saveButton.setEnabled(True)

    def getConfirmedData(self):
        return self.apiKeyEdit.text()

    def save(self):
        '''
        Send scale and unit values entered by user back to mouse tracker
        screen when save button is clicked.
        '''
        self.accept()
        self.close()

    def cancel(self):
        '''
        Return to mouse tracker screen if cancel button is clicked
        '''
        self.reject()
        self.close()

class ProjectSettingsWindow(QDialog):
    def __init__(self, parent=None):
        super(ProjectSettingsWindow, self).__init__(parent)

        self.setWindowTitle('Edit Project Data')
        self.setAttribute(Qt.WA_QuitOnClose, False)
        self.setModal(True)
        self.initUI()

    def initUI(self):
        '''
        Setup GUI elements of scale window
        '''
        mainLayout = QVBoxLayout()

        self.nameEdit = LineEdit()
        self.nameEdit.setPlaceholderText('Project Name')
        self.nameEdit.setValidator(QRegExpValidator(QRegExp('[^\\\*<>:"/\|?*]+')))
        self.nameEdit.textChanged.connect(self.checkFields)

        #horizontal layout containing save and cancel buttons
        hLayout = QHBoxLayout()
        self.saveButton = Button('Save')
        self.saveButton.clicked.connect(self.save)

        self.cancelButton = Button('Cancel')
        self.cancelButton.clicked.connect(self.cancel)

        hLayout.addWidget(self.saveButton)
        hLayout.addWidget(self.cancelButton)

        mainLayout.addWidget(self.nameEdit)
        mainLayout.addLayout(hLayout)
    
        self.setLayout(mainLayout)
        self.setModal(True)
        self.show()

    def checkFields(self):
        '''
        Check if all mandatory fields are entered
        '''
        if self.nameEdit.text():
            self.saveButton.setEnabled(True)
        else:
            self.saveButton.setEnabled(False)

    def save(self):
        '''
        Send data back to MainWindow to update project data
        '''
        self.parent().setProjectName(self.nameEdit.text())
        self.close()

    def cancel(self):
        '''
        Return to mouse tracker screen if cancel button is clicked
        '''
        self.close()

class MapWindow(QWidget):
    def __init__(self, api, ref, points):
        super(MapWindow, self).__init__()
        qInstallMessageHandler(lambda *args: None)
        self.api = api
        self.ref = ref
        self.points = points

        self.resize(1080, 768)
        self.initUI()

    def initUI(self):
        '''
        Setup GUI elements of scale window
        '''
        layout = QVBoxLayout()
        self.mapView = QWebEngineView()

        self.webchannel = QWebChannel(self.mapView)
        self.mapView.page().setWebChannel(self.webchannel)
        self.webchannel.registerObject('backend', self)

        current_dir = os.path.dirname(os.path.realpath(__file__))
        filename = os.path.join(current_dir, '.\Resources\index.html')
        self.mapView.load(QUrl.fromLocalFile(filename))

        layout.addWidget(self.mapView)
        self.setLayout(layout)
    
    @pyqtSlot(result=list)
    def getCenter(self):
        avgLat = mean([lat for lat,_ in self.ref])
        avgLon = mean([lon for _,lon in self.ref])

        return [{'lat': avgLat, 'lng': avgLon}]

    #pass reference point to index.html
    @pyqtSlot(result=list)
    def getRef(self):
        return [{'lat': lat, 'lng': lng} for lat, lng in self.ref]

    #pass point data to index.html
    @pyqtSlot(result=list)
    def getPoints(self):
        gmapsPoints = [{
            'Point': {'lat': p['Latitude'], 'lng': p['Longitude']},
            'Description': p['Description'],
            'Date': p['Date']
        } for p in self.points]

        return gmapsPoints

    #pass api key to index.html
    @pyqtSlot(result=str)
    def getAPIKey(self):
        return self.api

    def update(self, api, ref, points):
        self.api = api
        self.ref = ref
        self.points = points
        self.mapView.page().runJavaScript('initMap()')

'''
About Window Class Containing Info About Project
'''
class AboutWindow(QDialog):
    def __init__(self):
        super(AboutWindow, self).__init__()
        self.setFixedSize(300,350)
        self.setWindowTitle('About This Project')
        self.initUI()
    
    def initUI(self):
        self.aboutlayout = QVBoxLayout()
        self.textbox = QLabel()
        self.textbox.setAlignment(Qt.AlignLeft)
        self.textbox.setWordWrap(True)
        self.textbox.setText('ABOUT THIS PROJECT:\n\n“MapReader” is a software application designed to read latitude and longitude coordinates from a physical map using a mouse as an input device. These coordinates can then be reviewed for analytical purposes and exported to a data file. The purpose of this software is enabling the user to find coordinates on a physical map when points are not easily located using latitude and longitude lines. The application is designed for field researchers, taking into consideration the unique limitations of being used outdoors on laptops and out of network range.\n\nAuthors: \n\tEvan Brittain\n\tGabriel Aguirre\n\tJoseph Donati\n\tRyan Swearingen\n\tRandall Plant\n\tBlake Carlisle\n\nVersion:  1.0')
        self.aboutlayout.addWidget(self.textbox)
        self.cancelButton = Button('Cancel')
        self.cancelButton.clicked.connect(self.cancel)
        self.aboutlayout.addWidget(self.cancelButton)
        self.setLayout(self.aboutlayout)
        self.show()

    def cancel(self):
        '''
        Return to mouse tracker screen if cancel button is clicked
        '''
        self.close()

class ReferenceSelectionWindow(QDialog):
    def __init__(self, points, parent=None):
        super(ReferenceSelectionWindow, self).__init__(parent)
        self.resize(450, 300)
        self.setWindowTitle('Select Reference Points')
        self.points = points
        self.tableData = [{'Latitude': lat, 'Longitude': lon} for lat, lon in points]
        self.setAttribute(Qt.WA_QuitOnClose, False)
        self.initUI()

    def initUI(self):
        '''
        Setup GUI elements of scale window
        '''
        mainLayout = QVBoxLayout()

        #horizontal layout containing save and cancel buttons
        h2Layout = QHBoxLayout()
        self.saveButton = Button('Trace')
        self.saveButton.clicked.connect(self.save)
        
        self.cancelButton = Button('Cancel')
        self.cancelButton.clicked.connect(self.cancel)

        h2Layout.addWidget(self.saveButton)
        h2Layout.addWidget(self.cancelButton)

        self.table = Table('Reference Points', self.tableData, checkable=True)

        mainLayout.addWidget(self.table)
        mainLayout.addLayout(h2Layout)
    
        self.setLayout(mainLayout)
        self.setModal(True)
        self.show()
    
    def save(self):
        '''
        Send reference point back to main window to be stored
        '''
        self.selectedData = self.table.getCheckedRowData()
        if not self.selectedData:
            return

        self.selectedData = [(item['Latitude'], item['Longitude']) for item in self.selectedData]
        self.accept()
        self.close()

    def cancel(self):
        self.close()

class StarterWindow(QDialog):
    def __init__(self, controller):
        super(StarterWindow, self).__init__()
        self.controller = controller
        self.setFixedSize(500, 600)
        self.setWindowTitle('Welcome to MapReader')
        self.aboutWindow = None
        self.initUI()

    def initUI(self):
        '''
        Setup GUI elements of scale window
        '''
        mainLayout = QVBoxLayout()

        #horizontal layout containing new and open buttons
        hLayout = QHBoxLayout()
        self.projectTable = QTableWidget(self)

        projects_data = self.controller.getAllProjectData()
        self.projectTable.setRowCount(len(projects_data))
        self.projectTable.setColumnCount(2)
        
        for i, project in enumerate(projects_data):
            self.projectTable.setItem(i,0, QTableWidgetItem(project.get('ProjectName')))
            self.projectTable.setItem(i,1, QTableWidgetItem(str(len(project.get('Points')))))
            
        self.projectTable.cellDoubleClicked.connect(self.openProjectDC)
        
        self.projectTable.setHorizontalHeaderLabels(["Projects", "No. Points"])
        header = self.projectTable.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeToContents)       
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.Stretch)

        self.newButton = Button('New')
        self.newButton.clicked.connect(partial(self.controller.newProject, self))

        self.openButton = Button('Open')
        self.openButton.clicked.connect(partial(self.controller.browseProjectsDir, self))

        self.aboutButton = Button('About')
        self.aboutButton.clicked.connect(self.aboutProject)
        
        mainLayout.addWidget(self.projectTable)
        hLayout.addWidget(self.newButton)
        hLayout.addWidget(self.openButton)
        hLayout.addWidget(self.aboutButton)

        mainLayout.addLayout(hLayout)
    
        self.setLayout(mainLayout)

        self.show()     

    def openProjectDC(self, row, column):
        item = self.projectTable.currentItem()
        
        projectName = item.text()
        if column == 0:
            self.hide()
            self.controller.openProject(projectName, self)
        
    def aboutProject(self):
        '''
        Show About Screen
        '''
        self.aboutScreen = AboutWindow()

if __name__=='__main__':
    import sys

    app = QApplication(sys.argv)
    window = ReferencePointTable([(1,2), (3,4), (5,6)])
    sys.exit(app.exec_())

