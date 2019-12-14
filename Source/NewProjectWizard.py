from PyQt5.QtCore import Qt, QDateTime, QRegExp
from PyQt5.QtWidgets import QWizard, QWizardPage, QLabel, QVBoxLayout, QGridLayout, QMessageBox
from PyQt5 import QtGui
from PyQt5.QtGui import QPixmap
from geopy import Point
from CustomQtObjects import LineEdit

#Class to display new project wizard
class NewProjectWizard(QWizard):
    def __init__(self, parent=None):
        super(NewProjectWizard, self).__init__(parent)
        
        self.addPage(self.createIntroPage())
        self.dataPage = WizardDataPage(self)
        self.addPage(self.dataPage)
        self.addPage(self.createConclusionPage())

        self.setWindowTitle('New Project Wizard')
        self.setModal(True)
        self.show()

    def createIntroPage(self):
        '''
        Create first page of wizard
        '''
        page = QWizardPage()
        page.setTitle("Welcome")

        label = QLabel(
                "Follow instructions to create new Map Reader project.")
        label.setWordWrap(True)

        layout = QVBoxLayout()
        layout.addWidget(label)
        page.setLayout(layout)

        return page

    def createConclusionPage(self):
        '''
        Create last page of wizard
        '''
        page = QWizardPage()
        page.setTitle("Conclusion")

        label = QLabel("Your project has been created")
        label.setWordWrap(True)

        layout = QVBoxLayout()
        layout.addWidget(label)
        page.setLayout(layout)

        return page

    def cancel(self):
        '''
        Return to starter screen when cancel is pressed
        '''
        if self.parent():
            self.parent().starterScreen()
        else:
            self.close()
        


#Class to setup wizard page for project name and reference point entry
class WizardDataPage(QWizardPage):
    def __init__(self, parent):
        super(WizardDataPage, self).__init__(parent)
        self.setupUI()

    def setupUI(self):
        self.setTitle("Project Data")
        self.setSubTitle("Please fill all fields.")

        self.nameLabel = QLabel("Project Name:")
        self.nameLineEdit = LineEdit()
        self.nameLineEdit.setValidator(QtGui.QRegExpValidator(QRegExp('[^\\\*<>:"/\|?*]+')))
        self.registerField('projectName*', self.nameLineEdit)

        self.refLabel = QLabel("Reference Point:")
        self.latLineEdit = LineEdit()
        self.latLineEdit.setPlaceholderText('Latitude')
        self.registerField('latitude*', self.latLineEdit)

        self.lonLineEdit = LineEdit()
        self.lonLineEdit.setPlaceholderText('Longitude')
        self.registerField('longitude*', self.lonLineEdit)

        self.mapGraphic = QLabel(self)
        self.pixmap = QPixmap('Resources/LatLongImg_v0.2.png')
        self.mapGraphic.setPixmap(self.pixmap)
        self.resize(self.pixmap.width(), self.pixmap.height())
        
        self.layout = QVBoxLayout()
        self.layout2 = QGridLayout()

        self.layout2.addWidget(self.nameLabel, 0, 0)
        self.layout2.addWidget(self.nameLineEdit, 0, 1, 1, 3)
        self.layout2.addWidget(self.refLabel, 1, 0)
        self.layout2.addWidget(self.latLineEdit, 1, 1)
        self.layout2.addWidget(self.lonLineEdit, 1, 2)

        self.layout.addLayout(self.layout2)
        self.layout.addWidget(self.mapGraphic)

        self.setLayout(self.layout)

    def getProjectName(self):
        '''
        Returns project name entered in nameLineEdit field
        '''
        return self.nameLineEdit.text()

    def getReferencePoint(self):
        '''
        Returns reference lat/lon as tuple from latLineEdit and lonLineEdit fields
        '''
        lat = self.latLineEdit.text()
        lon = self.lonLineEdit.text()

        try:
            point = Point(lat + ' ' + lon)
        except:
            QMessageBox.information(
                    self,
                    'Reference Point Error',
                    f'Invalid reference point: ({lat}, {lon})'
                )
            return False
        else:
            lat = round(point.latitude, 6)
            lon = round(point.longitude, 6)
            return [(lat, lon)]