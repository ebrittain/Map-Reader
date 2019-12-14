from Map_Reader.ProjectController import ProjectController
from PyQt5 import QtCore
from PyQt5.QtWidgets import QWizard, QMessageBox
import time
import pytest
import os
import time
import shutil
import pyautogui
from datetime import date

path = os.path.dirname(os.path.realpath(__file__))
project_name = 'Test_Project'

def test_1(qtbot, mocker):
    '''
    Test normal operation of new project wizard from starter page
    '''
    mocker.patch.object(QMessageBox, 'information', return_value=QMessageBox.Ok)
    mocker.patch.object(QMessageBox, 'question', return_value=QMessageBox.Yes)
    pc = ProjectController()
    
    #|-------------------------------Creating Project---------------------------|#
    #Create new project
    def new_project_action():
        #Intro page
        qtbot.mouseClick(pc.npw.button(QWizard.NextButton), QtCore.Qt.LeftButton)

        #Data page
        qtbot.keyClicks(pc.npw.dataPage.nameLineEdit, project_name)
        qtbot.keyClicks(pc.npw.dataPage.latLineEdit, '38.12345')
        qtbot.keyClicks(pc.npw.dataPage.lonLineEdit, '-121.12345')
        qtbot.mouseClick(pc.npw.button(QWizard.NextButton), QtCore.Qt.LeftButton)

        #Conclusion page
        qtbot.mouseClick(pc.npw.button(QWizard.FinishButton), QtCore.Qt.LeftButton)
    
    QtCore.QTimer.singleShot(0, new_project_action)
    qtbot.mouseClick(pc.sw.newButton, QtCore.Qt.LeftButton)

    assert os.path.exists(f'../Projects/{project_name}')
    assert os.path.exists(f'../Projects/{project_name}/Reports')
    assert os.path.exists(f'../Projects/{project_name}/project_data.json')

    assert pc.mw.reference[0][0] == 38.12345
    assert pc.mw.reference[0][1] == -121.12345

    #|--------------------------Core Functionality--------------------------------|#
    #Add new reference point
    def add_ref_action():
        ref_add_win = pc.mw.refWindow

        qtbot.keyClicks(ref_add_win.latEdit, '38.54321')
        qtbot.keyClicks(ref_add_win.lonEdit, '-121.54321')
        qtbot.mouseClick(ref_add_win.saveButton, QtCore.Qt.LeftButton)

    QtCore.QTimer.singleShot(0, add_ref_action)
    qtbot.mouseClick(pc.mw.addRefButton, QtCore.Qt.LeftButton)
    assert pc.mw.reference[1][0] == 38.54321
    assert pc.mw.reference[1][1] == -121.54321

    #Set scale
    qtbot.mouseClick(pc.mw.setScaleButton, QtCore.Qt.LeftButton)
    qtbot.waitUntil(pc.mw.scaleTrace.isVisible)
    x, y = pc.mw.scaleTrace.getCenter()
    start_pos, end_pos = QtCore.QPoint(x, y), QtCore.QPoint(x + 800, y)

    def confirm_scale_action():
        scale_win = pc.mw.scaleConfirm

        scale_win.scaleEdit.clear()
        qtbot.keyClicks(scale_win.scaleEdit, '5')
        qtbot.mouseClick(scale_win.saveButton, QtCore.Qt.LeftButton)

    def on_value_changed(value):
        QtCore.QTimer.singleShot(200, confirm_scale_action)
        pyautogui.dragTo(value.x(), value.y(), button='left')

    animation = QtCore.QVariantAnimation(
        startValue=start_pos,
        endValue=end_pos,
        duration=100
    )
    pyautogui.moveTo(start_pos.x(), start_pos.y())
    pyautogui.mouseDown(button='left')
    animation.valueChanged.connect(on_value_changed)
    with qtbot.waitSignal(animation.finished):
        animation.start()

    assert pc.mw.scale == 800/5
    assert pc.mw.units == 'km'
    
    #Add point manually
    def man_point_action():
        man_add_win = pc.mw.manualAddWindow

        qtbot.keyClicks(man_add_win.latEdit, '38.23456')
        qtbot.keyClicks(man_add_win.lonEdit, '-121.23456')
        qtbot.keyClicks(man_add_win.descBox, 'Test description for manually added point')
        qtbot.mouseClick(man_add_win.saveButton, QtCore.Qt.LeftButton)

    QtCore.QTimer.singleShot(0, man_point_action)
    qtbot.mouseClick(pc.mw.manPointButton, QtCore.Qt.LeftButton)
    assert pc.mw.points[0]['Latitude'] == 38.23456
    assert pc.mw.points[0]['Longitude'] == -121.23456
    assert pc.mw.points[0]['Description'] == 'Test description for manually added point'

    #Trace point
    def ref_selection_action():
        ref_select_win = pc.mw.referenceTable
        ref_select_win.table.sourceModel.item(0, 0).setCheckState(True)
        qtbot.mouseClick(ref_select_win.saveButton, QtCore.Qt.LeftButton)

    def confirm_loc_action():
        loc_win = pc.mw.locationConfirm
        qtbot.keyClicks(loc_win.descBox, 'Test description for traced point')
        qtbot.mouseClick(loc_win.saveButton, QtCore.Qt.LeftButton)

    def on_value_changed_loc(value):
        QtCore.QTimer.singleShot(200, confirm_loc_action)
        pyautogui.dragTo(value.x(), value.y(), button='left')

    QtCore.QTimer.singleShot(0, ref_selection_action)
    qtbot.mouseClick(pc.mw.traceButton, QtCore.Qt.LeftButton)
    qtbot.waitUntil(pc.mw.locationTrace.isVisible)

    x, y = pc.mw.locationTrace.getCenter()
    start_pos, end_pos = QtCore.QPoint(x, y), QtCore.QPoint(x + 800, y + 800)

    animation = QtCore.QVariantAnimation(
        startValue=start_pos,
        endValue=end_pos,
        duration=100
    )
    pyautogui.moveTo(start_pos.x(), start_pos.y())
    pyautogui.mouseDown(button='left')
    animation.valueChanged.connect(on_value_changed_loc)
    with qtbot.waitSignal(animation.finished):
        animation.start()
    
    assert isinstance(pc.mw.points[1]['Latitude'], float)
    assert isinstance(pc.mw.points[1]['Longitude'], float)
    assert pc.mw.points[1]['Description'] == 'Test description for traced point'

    #|--------------------------Menu Bar Testing----------------------------------|#
    #Mouse settings window
    pc.mw.menuMouseSettings.trigger()
    orig_sens = pc.mw.mouseSettingsWindow.sl.value()
    orig_accel = pc.mw.mouseSettingsWindow.checkBox.isChecked()

    pc.mw.mouseSettingsWindow.sl.setValue(15)
    pc.mw.mouseSettingsWindow.checkBox.setChecked(True)
    qtbot.mouseClick(pc.mw.mouseSettingsWindow.saveButton, QtCore.Qt.LeftButton)

    pc.mw.menuMouseSettings.trigger()
    assert pc.mw.mouseSettingsWindow.sl.value() == 15
    assert pc.mw.mouseSettingsWindow.checkBox.isChecked()

    pc.mw.mouseSettingsWindow.sl.setValue(orig_sens)
    pc.mw.mouseSettingsWindow.checkBox.setChecked(orig_accel)
    qtbot.mouseClick(pc.mw.mouseSettingsWindow.saveButton, QtCore.Qt.LeftButton)

    #refresh
    pc.mw.menuRefresh.trigger()
    assert pc.mw.isActiveWindow()

    #themes
    orig_theme = pc.settings['Theme']

    pc.mw.themeBlack.trigger()
    assert pc.settings['Theme'] == 'Black'

    pc.mw.themeGreen.trigger()
    assert pc.settings['Theme'] == 'Green'

    pc.mw.themeBlue.trigger()
    assert pc.settings['Theme'] == 'Blue'

    pc.mw.themeDefault.trigger()
    assert not pc.settings['Theme']

    pc.settings['Theme'] = orig_theme

    #exporting data
    dt = date.strftime(date.today(), '%m-%d-%y')

    pc.mw.exportCSV.trigger()
    assert os.path.exists(f'../Projects/{project_name}/Reports/{dt}_Report.csv')

    pc.mw.exportJSON.trigger()
    assert os.path.exists(f'../Projects/{project_name}/Reports/{dt}_Report.json')

    pc.mw.exportExcel.trigger()
    assert os.path.exists(f'../Projects/{project_name}/Reports/{dt}_Report.xlsx')

    pc.mw.exportHTML.trigger()
    assert os.path.exists(f'../Projects/{project_name}/Reports/{dt}_Report.html')

    #edit project data
    pc.mw.menuProjectSettings.trigger()
    qtbot.keyClicks(pc.mw.projectSettingsWindow.nameEdit, 'New_Test_Project')
    qtbot.mouseClick(pc.mw.projectSettingsWindow.saveButton, QtCore.Qt.LeftButton)

    assert os.path.exists('../Projects/New_Test_Project')

    os.rename('../Projects/New_Test_Project', f'../Projects/{project_name}')
    assert os.path.exists(f'../Projects/{project_name}')

    #add api key
    orig_api = pc.settings['API']

    def api_action():
        qtbot.keyClicks(pc.mw.apiKeyWindow.apiKeyEdit, 'ABCDEF')
        qtbot.mouseClick(pc.mw.apiKeyWindow.saveButton, QtCore.Qt.LeftButton)

    QtCore.QTimer.singleShot(0, api_action)
    pc.mw.menuAPISettings.trigger()

    assert pc.settings['API'] == 'ABCDEF'

    pc.setAPI(orig_api)
    assert pc.settings['API'] == orig_api

    #close project
    pc.mw.menuClose.trigger()
    assert not pc.mw.isActiveWindow()
    assert pc.sw.isActiveWindow()

    #delete test project
    shutil.rmtree(f'../Projects/{project_name}')
    assert not os.path.exists(f'../Projects/{project_name}')
    