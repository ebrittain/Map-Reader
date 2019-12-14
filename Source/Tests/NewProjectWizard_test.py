from Map_Reader.NewProjectWizard import NewProjectWizard
from PyQt5 import QtCore
from PyQt5.QtWidgets import QWizard
import pytest
import time

@pytest.fixture
def window():
    window = NewProjectWizard()
    return window

def test_1(qtbot, window):
    '''
    Test if pressing cancel closes window
    '''
    qtbot.mouseClick(window.button(QWizard.CancelButton), QtCore.Qt.LeftButton)

    assert window.isActiveWindow() == False

def test_2(qtbot, window):
    '''
    Test normal operation
    '''
    #Intro page
    qtbot.mouseClick(window.button(QWizard.NextButton), QtCore.Qt.LeftButton)

    #Data page
    qtbot.keyClicks(window.dataPage.nameLineEdit, 'Test Project')
    qtbot.keyClicks(window.dataPage.latLineEdit, '38.12345')
    qtbot.keyClicks(window.dataPage.lonLineEdit, '-121.12345')
    qtbot.mouseClick(window.button(QWizard.NextButton), QtCore.Qt.LeftButton)

    #Conclusion page
    qtbot.mouseClick(window.button(QWizard.FinishButton), QtCore.Qt.LeftButton)

    assert window.isActiveWindow() == False

def test_3(qtbot, window):
    '''
    Test next is disabled when project name is blank
    '''
    qtbot.mouseClick(window.button(QWizard.NextButton), QtCore.Qt.LeftButton)

    qtbot.keyClicks(window.dataPage.latLineEdit, '38.12345')
    qtbot.keyClicks(window.dataPage.lonLineEdit, '-121.12345')

    assert window.button(QWizard.NextButton).isEnabled() == False

def test_4(qtbot, window):
    '''
    Test next is disabled when lat field is blank
    '''
    qtbot.mouseClick(window.button(QWizard.NextButton), QtCore.Qt.LeftButton)

    qtbot.keyClicks(window.dataPage.nameLineEdit, 'Test Project')
    qtbot.keyClicks(window.dataPage.lonLineEdit, '-111.12345')

    assert window.button(QWizard.NextButton).isEnabled() == False

def test_5(qtbot, window):
    '''
    Test next is disabled when lon field is blank
    '''
    qtbot.mouseClick(window.button(QWizard.NextButton), QtCore.Qt.LeftButton)

    qtbot.keyClicks(window.dataPage.nameLineEdit, 'Test Project')
    qtbot.keyClicks(window.dataPage.latLineEdit, '-30.12345')

    assert window.button(QWizard.NextButton).isEnabled() == False

def test_6(qtbot, window):
    '''
    Test regex properly validates project name field
    '''
    qtbot.mouseClick(window.button(QWizard.NextButton), QtCore.Qt.LeftButton)

    qtbot.keyClicks(window.dataPage.nameLineEdit, '**Te\\st<>: Pr??oject')

    assert window.dataPage.nameLineEdit.text() == 'Test Project'
