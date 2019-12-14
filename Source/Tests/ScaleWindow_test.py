from Map_Reader.Windows import ScaleWindow
from PyQt5 import QtCore
import pytest

@pytest.fixture
def window():
    window = ScaleWindow(100)
    return window

def test_1(qtbot, window):
    '''
    Test if all field are populated and save button is enabled by default
    '''
    qtbot.addWidget(window)
    
    assert window.pixelEdit.text() == '100'
    assert window.scaleEdit.text() == '1'
    assert window.comboBox.currentText() == 'km'
    assert window.saveButton.isEnabled() == True

def test_2(qtbot, window):
    '''
    Test that fields are properly entered and limited to two decmals
    '''
    qtbot.addWidget(window)
    window.pixelEdit.setText(None)
    window.scaleEdit.setText(None)

    qtbot.keyClicks(window.pixelEdit, '4932.343')
    qtbot.keyClicks(window.scaleEdit, '35')
    
    assert window.pixelEdit.text() == '4932.34'
    assert window.scaleEdit.text() == '35'

def test_3(qtbot, window):
    '''
    Test save button is disabled when no data is entered
    '''
    qtbot.addWidget(window)
    window.pixelEdit.setText(None)
    window.scaleEdit.setText(None)

    assert window.saveButton.isEnabled() == False

def test_4(qtbot, window):
    '''
    Test save button is disabled when only scale data is entered
    '''
    qtbot.addWidget(window)
    window.pixelEdit.setText(None)

    assert window.saveButton.isEnabled() == False

def test_5(qtbot, window):
    '''
    Test save button is disabled when only pixel data is entered
    '''
    qtbot.addWidget(window)
    window.scaleEdit.setText(None)

    assert window.saveButton.isEnabled() == False

def test_6(qtbot, window):
    '''
    Test that window is still open after erroneous data is entered
    and save is pressed
    '''
    qtbot.addWidget(window)
    window.pixelEdit.setText(None)
    window.scaleEdit.setText(None)

    qtbot.keyClicks(window.pixelEdit, '0')
    qtbot.keyClicks(window.scaleEdit, '-1.374')
    qtbot.mouseClick(window.saveButton, QtCore.Qt.LeftButton)

    assert window.isActiveWindow() == True
    window.close()

def test_7(qtbot, window):
    '''
    Test that window is closed when cancel is pressed
    '''
    qtbot.mouseClick(window.cancelButton, QtCore.Qt.LeftButton)

    assert window.isActiveWindow() == False
