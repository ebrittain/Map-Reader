from Map_Reader.Windows import StarterWindow
from Map_Reader.ProjectController import ProjectController
from PyQt5.QtWidgets import QWizard
from PyQt5 import QtCore
import pytest
import time

@pytest.fixture
def window():
    window = StarterWindow(ProjectController())
    return window

def test_1(qtbot, window):
    '''
    Test if the about page loads
    '''
    qtbot.mouseClick(window.aboutButton, QtCore.Qt.LeftButton)
    assert window.aboutScreen.isActiveWindow() == True
    window.close()

def test_2(qtbot, window):
    '''
    Test if the about page exits properly
    '''
    qtbot.mouseClick(window.aboutButton, QtCore.Qt.LeftButton)
    qtbot.mouseClick(window.aboutScreen.cancelButton, QtCore.Qt.LeftButton)

    assert window.aboutScreen.isActiveWindow() == False

def test_3(qtbot, window):
    '''
    Test creating a new project and going to new project wizard
    '''

    pc = ProjectController()

    def on_timeout():


        assert pc.npw.isActiveWindow() == True

        qtbot.mouseClick(pc.npw.button(QWizard.CancelButton), QtCore.Qt.LeftButton)

        assert pc.npw.isActiveWindow() == False


    QtCore.QTimer.singleShot(0, on_timeout)
    qtbot.mouseClick(pc.sw.newButton, QtCore.Qt.LeftButton)