from Map_Reader.Windows import ReferenceWindow
from PyQt5 import QtCore
from PyQt5.QtWidgets import QMessageBox
import pytest

@pytest.fixture
def window():
    window = ReferenceWindow()
    return window

def test_1(qtbot, window):
    '''
    Test if setting reference point data is correctly passed
    and stored in reference tuple from main window when save
    button is pressed
    '''
    qtbot.addWidget(window)
    
    qtbot.keyClicks(window.latEdit, '37.343')
    qtbot.keyClicks(window.lonEdit, '121.343')
    qtbot.mouseClick(window.saveButton, QtCore.Qt.LeftButton)

    assert window.latEdit.text() == '37.343'
    assert window.lonEdit.text() == '121.343'

def test_2(qtbot, window):
    '''
    Test if save button in referene window is disabled when only
    lat input is entered
    '''
    qtbot.addWidget(window)
    
    qtbot.keyClicks(window.latEdit, '70.123')

    assert window.saveButton.isEnabled() == False

def test_3(qtbot, window):
    '''
    Test if save button in referene window is disabled when only
    lon input is entered
    '''
    
    qtbot.keyClicks(window.lonEdit, '121.1234')

    assert window.saveButton.isEnabled() == False

def test_4(qtbot, mocker, window):
    '''
    Test that window is still open after erroneous data is entered
    and save is pressed
    '''
    mocker.patch.object(QMessageBox, 'information', return_value=QMessageBox.Ok)
    qtbot.keyClicks(window.latEdit, '91.343')
    qtbot.keyClicks(window.lonEdit, '-7000.343')
    qtbot.mouseClick(window.saveButton, QtCore.Qt.LeftButton)

    assert window.isActiveWindow() == True

def test_5(qtbot, window):
    '''
    Test that window is closed when cancel is pressed
    '''
        
    qtbot.keyClicks(window.latEdit, '37.343')    
    qtbot.keyClicks(window.lonEdit, '121.343')
    qtbot.mouseClick(window.cancelButton, QtCore.Qt.LeftButton)

    assert window.isActiveWindow() == False