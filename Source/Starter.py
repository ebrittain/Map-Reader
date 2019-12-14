from PyQt5.QtWidgets import QApplication
from ProjectController import ProjectController

if __name__ == '__main__':

    import sys

    app = QApplication(sys.argv)
    window = ProjectController()
    sys.exit(app.exec_())