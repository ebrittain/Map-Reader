import os

from MainWindow import MainWindow
from NewProjectWizard import NewProjectWizard
from Windows import StarterWindow

from PyQt5.QtCore import Qt, QDateTime, QStringListModel, QDate
from PyQt5.QtWidgets import qApp, QMessageBox, QFileDialog
from PyQt5 import QtGui
import pandas as pd
import json

DIR_NAME = os.path.abspath(os.path.dirname(__file__))
SETTINGS_DIR = os.path.join(DIR_NAME, 'Settings')
SETTINGS_PATH = os.path.join(SETTINGS_DIR, 'settings.json')
PROJECTS_DIR = os.path.join(DIR_NAME, 'Projects')
RESOURCES_DIR = os.path.join(DIR_NAME, 'Resources')

class ProjectController():
    def __init__(self):
        icon_path = os.path.join(RESOURCES_DIR, 'icons', 'app_icon.png')
        qApp.setWindowIcon(QtGui.QIcon(icon_path))
  
        if not os.path.exists(PROJECTS_DIR):
            os.mkdir(PROJECTS_DIR)
        if not os.path.exists(SETTINGS_DIR):
            self.createSettingsFile()

        self.loadSettings()
        self.sw = StarterWindow(self)
        self.mw = None
    
    def loadSettings(self):
        '''
        Load default user settings
        '''
        with open(SETTINGS_PATH, 'rt') as f:
            self.settings = json.loads(f.read())

        self.loadTheme(self.settings.get('Theme'))

    def saveSettings(self):
        '''
        Save updated settings data 
        '''
        try:
            with open(SETTINGS_PATH, 'w+') as f:
                f.write(json.dumps(self.settings))
        except:
            return False
        else:
            return True

    def loadTheme(self, theme=None):
        '''
        Load given theme and save to settings file
        '''
        if theme:
            theme_path = os.path.join(RESOURCES_DIR, f'stylesheet_{theme}.css')
            with open(theme_path, 'rt') as f:
                qApp.setStyleSheet(f.read())
        else:
            qApp.setStyleSheet(None)

        self.settings['Theme'] = theme
        self.saveSettings()

    def setAPI(self, api_key):
        '''
        Save api key to settings file
        '''
        self.settings['API'] = api_key
        return self.saveSettings()


    def createSettingsFile(self):
        '''
        Create settings directory and settings.json file if it doesn't exist
        this function should only be called on first launch of application
        '''
        default_data = {
            'Theme': None,
            'API': None
        }
        os.mkdir(SETTINGS_DIR)
        with open(SETTINGS_PATH, 'w+') as f:
            f.write(json.dumps(default_data))

    def newProject(self, window_ref):
        '''
        window_ref: (QDialog) reference to the window that function is called from
        '''
        self.npw = NewProjectWizard()
        
        if self.npw.exec_():
            project_name = self.npw.dataPage.getProjectName()
            ref = self.npw.dataPage.getReferencePoint()
            if project_name and ref:
                self.createProject(window_ref, project_name, ref)

    def createProject(self, window_ref, project_name, ref):
        '''
        window_ref: (QDialog) reference to the window that function is called from 
        project_name: (str) name of new project
        ref: (tuple) reference point 
        '''    
        project_file = os.path.join(PROJECTS_DIR, project_name, 'project_data.json')
        created_date = QDateTime().currentDateTime().toString('MM-dd-yyyy hh:mm:ss ap')
        default_data = {
                'ProjectName': project_name,
                'Created': created_date,
                'LastAccessed': created_date,
                'Reference': ref,
                'Scale': 0,
                'Units': '',
                'Points': []
        }
        try:
            os.makedirs(os.path.join(PROJECTS_DIR, project_name, 'Reports'))
            with open(project_file, 'w+') as f:
                f.write(json.dumps(default_data))

        except FileExistsError:
            QMessageBox.critical(
                window_ref,
                'Project Creation Error',
                f'Invalid project name: {project_name}'
            )
        else:
            window_ref.close()
            self.mw = MainWindow(project_name, self, openExisting=True, api=self.settings.get('API'))

    def closeProject(self):
        '''
        Close the currently open projects and redisplay starter window
        '''
        self.mw.close()
        self.sw = StarterWindow(self)

    def browseProjectsDir(self, window_ref):
        fileDialog = QFileDialog(window_ref, 'Projects', PROJECTS_DIR)
        fileDialog.setFileMode(QFileDialog.DirectoryOnly)
        fileDialog.setAttribute(Qt.WA_QuitOnClose, False)

        #If a valid path is returned from file dialog screen
        if fileDialog.exec_():
            selected_path = fileDialog.selectedFiles()[0]
            #Check if json data file is in selected folder
            projectName = selected_path.split('/')[-1]
            self.openProject(projectName, window_ref)

    def openProject(self, project_name, window_ref):
        '''
        window_ref: (QDialog) a reference to the window that called this function
        '''
        path = os.path.join(PROJECTS_DIR, project_name, 'project_data.json')
        
        if os.path.exists(path):
            window_ref.close()
            self.mw = MainWindow(project_name, self, openExisting=True, api=self.settings.get('API'))
            #alert for invalid project and return to main window or starter screen
        else:
            QMessageBox.critical(
                window_ref,
                'Export File',
                f'{project_name} file failed to be created'
            )
               
    def saveProject(self, project_name, project_data):
        '''
        Saves the project data in json format and writes to a file
        '''
        project_path = os.path.join(PROJECTS_DIR, project_name, 'project_data.json')

        try:
            with open(project_path, 'w+') as f:
                f.write(json.dumps(project_data, indent=2))
        except:
            return False
        else:
            return True

    def setProjectName(self, old_name, new_name):
        '''
        Rename project
        '''
        old_path = os.path.join(PROJECTS_DIR, old_name)
        new_path = os.path.join(PROJECTS_DIR, new_name)

        try:
            os.rename(old_path, new_path)
        except:
            return False
        else:
            return True
    
    def exportProjectData(self, project_name, data, file_type):
        '''
        '''
        df = pd.DataFrame(data)
        path = os.path.join(PROJECTS_DIR, project_name, 'Reports', QDate.currentDate().toString("MM-dd-yy") + f'_Report.{file_type}')

        try:
            if file_type == 'csv':
                df.to_csv(path, index=False)
            elif file_type == 'json':
                df.to_json(path)
            elif file_type == 'xlsx':
                df.to_excel(path, index=False)
            elif file_type == 'html':
                df.to_html(path, index=False)
            else:
                raise ValueError   
        except:
            return False
        else:
            return True
    
    def getProjectData(self, project_name):

        path = os.path.join(PROJECTS_DIR, project_name, 'project_data.json')

        try:
            with open(path, 'r') as f:
                data = json.loads(f.read())
        except:
            return False
        else:
            return data

    def getAllProjectData(self):

        project_names = self.getProjects()
        data = []

        for name in project_names:
            data.append(self.getProjectData(name))

        return data

    def getProjects(self):
        '''
        Return list of project names within Projects directory
        '''
        return [f.name for f in os.scandir(PROJECTS_DIR) if f.is_dir()]