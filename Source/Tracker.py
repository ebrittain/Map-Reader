from PyQt5.QtCore import Qt, QDateTime
from PyQt5.QtWidgets import QLabel, QMessageBox, QApplication, QDialog, QWidget
from PyQt5.QtGui import QCursor, QFont
from geopy.distance import geodesic
from collections import namedtuple
import math
from MouseController import MouseController
import numpy as np
import pandas as pd

from CustomQtObjects import *

#Create namedtuple for readability to store point data
Point = namedtuple('Point', 'x y')

#Tracker class to handle mouse movement for locating point and setting scale
#Two modes: scale and location
class Tracker(QDialog):

    def __init__(self, parent=None, hidden=True):
        super(Tracker, self).__init__(parent)

        self.hidden = hidden

        self.mouseController = MouseController()
        self.origMouseSpeed = self.mouseController.getSpeed()
        self.origAcceleration = self.mouseController.getAcceleration()

        self.zeroVariables()
           
        self.cursor = QCursor()
        self.initUI()
        
    
    def initUI(self):
        '''
        Setup GUI elements of mouse tracker screen.
        '''      
        grid = QGridLayout()
        grid.setContentsMargins(80, 80, 80, 80)

        self.displayBox = ScaleDisplayWidget()      
        grid.addWidget(self.displayBox, 0, 0, Qt.AlignTop)
        grid.addWidget(QLabel(''), 0, 1, Qt.AlignTop)
        self.setLayout(grid)
        self.setWindowTitle('Scale')
        self.showFullScreen()
        self.setModal(True)
        QMessageBox.information(
            self,
            'Tracing Prompt',
            'Begin tracing scale',
            QMessageBox.Ok
        )
        
        
    def getCenter(self):
        '''
        Find the center point of the window by adding half the distance of
        the height and width to the absolute x, y location of the window.
        '''
        #Reference to geometry of screen and cursor
        geo = self.geometry()
        cur = self.cursor
        
        #Get x, y coords of the screen, left upper corner
        x_pos = geo.x()
        y_pos = geo.y()
            
        #Get width and height of screen distances from left upper corner
        width = geo.width()
        height = geo.height()
            
        #Find center point of screen
        x_center = x_pos + (width//2)
        y_center = y_pos + (height//2)
        
        return Point(x_center, y_center)
    
    def getCursorPos(self):
        '''
        Return the current position of the cursor relative to the upper
        left corner of the window.
        '''
        x = self.cursor.pos().x()
        y = self.cursor.pos().y()
        
        return Point(x, y)

    def getDX(self):
        '''
        Calculate distance from center in x direction
        '''
        center = self.getCenter()
        curPos = self.getCursorPos()

        return curPos.x - center.x

    def getDY(self):
        '''
        Calculate distance from center in y direction
        '''
        center = self.getCenter()
        curPos = self.getCursorPos()

        #reverse y for inverted y-axis
        return center.y - curPos.y

    def getDistance(self, dx, dy):
        '''
        Calculate straight line distance from point a to b using net distance
        in x and y direction

        Args:
            dx (float): total distance in pixels traveled in x direction
            dy (float): total distance in pixels traveled in y direction
        
        Returns:
            Total distance
        '''
        try:
            return round(math.sqrt(dx**2 + dy**2), 6)
        except:
            return 0

    def getBearing(self, dx, dy):
        '''
        Calculate the bearing of the mouse movement

        Args:
            dx (float): total distance in pixels traveled in x direction
            dy (float): total distance in pixels traveled in y direction

        Returns:
            bearing (float): bearing in degrees
        '''
        try:
            bearing = math.degrees(math.atan2(dy, dx))

        except Exception as e:
            print('Error: getBearing:', e.__class__.__name__)
            #do something to handle error
            return 1

        else:
            #shift bearing so 0 degrees is now grid north
            bearing = (360 + (90 - bearing)) % 360

            return round(bearing, 6)
    
    def convert(self, dist, scale):
        '''
        Convert distance in pixels to unit of measurement (km, mi, etc...)

        Args:
            dist (float): Euclidean distances from start to end point
            scale (int): scale to convert pixels to proper units

        Returns:
            convDist (float): converted mouse movement in correct unit of measurement
        '''
        try:
            convDist = dist / scale

        except Exception as e:
            print('Error: convert:', e.__class__.__name__)
            #do something to handle error
            return 1

        else:
            return round(convDist, 6)
    
    def newLocation(self, ref, dist, bearing):
        '''
        Computes the latitude and longitude using mouse movements distance
        and bearing from a reference point

        Args:
            ref (tuple): latitude and longitude of the reference point
            dist (float): converted euclidean distance of mouse movement
            bearing (float): bearing in degrees of mouse movement

        Returns:
            coords.latitude (float): latitude of new location
            coords.longitude(float): longitude of new location
        '''
        #kilometers
        if self.units == 'km':
            coords = geodesic(kilometers=dist).destination(ref, bearing)
        #miles    
        elif self.units == 'mi':
            coords = geodesic(miles=dist).destination(ref, bearing)
        #meters        
        elif self.units == 'm':
            coords = geodesic(meters=dist).destination(ref, bearing)
        #feet    
        elif self.units == 'ft':
            coords = geodesic(feet=dist).destination(ref, bearing)
        return Point(round(coords.latitude, 6), round(coords.longitude, 6))
    
    def zeroVariables(self):
        '''
        Zero out all instance variables after mouse has been released.
        '''
        self.dx = 0
        self.dy = 0
        self.temp_dx = 0
        self.temp_dy = 0
        self.dist = 0
        self.dist_px = 0
        self.bearing = 0
        self.newLoc = Point(0, 0)

    def resetTrace(self):
        '''
        Reset reference points if user needs to trace again
        '''
        self.zeroVariables()
        self.updateLabel()

    def updateLabel(self):
        '''
        Constantly update data on window label
        '''
        dx_update = self.dx + self.temp_dx
        dy_update = self.dy + self.temp_dy
        dist_update = self.dist_px
        
        self.displayBox.update(dx_update, dy_update, dist_update)

    def update(self):
        '''
        Tracks current x and y distance and updates label
        '''
        geo = self.geometry()
        cur = self.cursor
        center = self.getCenter()
        
        #Get current x, y, and straight line distance from center
        self.temp_dx = self.getDX()
        self.temp_dy = self.getDY()
        self.dist_px = self.getDistance(self.dx + self.temp_dx, self.dy + self.temp_dy)

        #Check if cursor is within window boundaries
        #Only update dx, dy instance variables when border has been reached
        curLoc = {cur.pos().x(), cur.pos().y()}
        boundaries = {0, geo.width()-1, geo.height()-1}

        if curLoc.intersection(boundaries):
            self.dx += self.temp_dx
            self.dy += self.temp_dy
            cur.setPos(center.x, center.y)

        self.updateLabel()
        
    def mousePressEvent(self, e):
        '''
        When mouse is pressed cursor will be repositioned at the center
        of the window and tracking will start.
        '''
        center = self.getCenter()
        self.cursor.setPos(center.x, center.y)

        #Max out mouse pointer speed
        #self.mouseController.setSpeed(20)

        #turn mouse acceleration off
        self.mouseController.setAcceleration(False)
                
        if self.hidden:
            QApplication.setOverrideCursor(Qt.CrossCursor)
        else:
            QApplication.setOverrideCursor(Qt.CrossCursor)
    
    def mouseReleaseEvent(self, e):
        '''
        When mouse is released cursor type will be reset or shown
        again if hidden.
        '''
        #update net dx, dy one more time
        self.dx += self.temp_dx
        self.dy += self.temp_dy

        #restore cursor type and zero out variables
        QApplication.restoreOverrideCursor()

        #Reset mouse speed to original setting
        self.mouseController.setSpeed(self.origMouseSpeed)

        #Reset mouse acceleration
        self.mouseController.setAcceleration(self.origAcceleration)
        
        self.parent().confirmScale(self.dist_px)
        return
        
    def mouseMoveEvent(self, e):
        '''
        When mouse button is pressed and moving all fields will be actively updated.
        The current distance x, y, and total from the center will be added to the 
        overall distance to track current bearing, distance, and current location.
        '''
        self.update()

class TrackerLoc(Tracker):

    def __init__(self, ref, scale, units, parent=None, hidden=True):
        self.ref = ref
        self.scale = scale
        self.units = units
        self.refIter = iter(ref)
        self.currentRef = next(self.refIter)
        self.traceData = []
        super(TrackerLoc, self).__init__(parent, hidden)

    def initUI(self):
        '''
        Setup GUI elements of mouse tracker screen.
        '''      
        grid = QGridLayout()
        grid.setContentsMargins(80, 80, 80, 80)

        self.displayBox = LocationDisplayWidget(self.units)          
        grid.addWidget(self.displayBox, 0, 0, Qt.AlignTop)
        grid.addWidget(QLabel(''), 0, 1, Qt.AlignTop)
        self.setLayout(grid)
        self.setWindowTitle('Location')
        self.showFullScreen()
        self.setModal(True)
        QMessageBox.information(
            self,
            'Tracing Prompt',
            'Begin tracing from first reference point:\n\n'+'Latitude: '+str(self.currentRef[0])+'\nLongitude: '+str(self.currentRef[1]),
            QMessageBox.Ok
        )

    def mouseReleaseEvent(self, e):
        '''
        When mouse is released cursor type will be reset or shown
        again if hidden.
        '''
        #update net dx, dy one more time
        self.dx += self.temp_dx
        self.dy += self.temp_dy

        #restore cursor type and zero out variables
        QApplication.restoreOverrideCursor()

        #Reset mouse speed to original setting
        self.mouseController.setSpeed(self.origMouseSpeed)

        #Reset mouse acceleration
        self.mouseController.setAcceleration(self.origAcceleration)
        
        data = {
            'Reference': (self.currentRef[0], self.currentRef[1]),
            'DX': self.dx,
            'DY': self.dy,
            'Distance_PX': self.dist_px,
            'Distance_Actual': self.dist,
            'Bearing': self.bearing,
            'New_Lat': self.newLoc[0],
            'New_Lon': self.newLoc[1],
            'Units': self.units 
        }
        self.traceData.append(data)
        self.zeroVariables()
        try:
            self.currentRef = next(self.refIter)
            QMessageBox.information(self,
                'Tracing Prompt',
                'Begin tracing from next reference point:\n\n'+'Latitude: '+str(self.currentRef[0])+'\nLongitude: '+str(self.currentRef[1]),
                QMessageBox.Ok
            )
        except StopIteration:
            self.averageData()
            self.parent().confirmLocation(self.newLoc.x, self.newLoc.y)
    
    def averageData(self, circle=False):
        '''
        Averaging master function
        '''
        if circle == True:
            df = pd.DataFrame(self.traceData, columns=['Reference', 'New_Lat', 'New_Lon'])
            df[['Reference_x', 'Reference_y']] = pd.DataFrame(df['Reference'].tolist(), index=df.index)
            df.drop('Reference', axis=1, inplace=True)
            df = df[['Reference_x', 'Reference_y', 'New_Lat', 'New_Lon']]
            df['Euclidean_Dist'] = self.convertEuclidean(df['Reference_x'], df['Reference_y'], df['New_Lat'], df['New_Lon'])
            df.drop(['New_Lat', 'New_Lon'], axis=1, inplace=True)
            final = []
            for row1 in df.itertuples(index=False):
                for row2 in df.itertuples(index=False):
                    dx = row2.Reference_x - row1.Reference_x
                    dy = row2.Reference_y - row1.Reference_y
                    d = math.sqrt((dx**2 + dy**2))
                    if row1 == row2:
                        print("Same Circle!")
                        continue
                    if d >= (row2.Euclidean_Dist + row1.Euclidean_Dist):
                        #Sure of this formula, derived it myself
                        print("Circles do not meet or meet at exactly 1 point!")
                        temp1X = row2.Reference_x + row2.Euclidean_Dist * ((row1.Reference_x - row2.Reference_x)/d)
                        temp1Y = row2.Reference_y + row2.Euclidean_Dist * ((row1.Reference_y - row2.Reference_y)/d)
                        temp2X = row1.Reference_x + row1.Euclidean_Dist * ((row2.Reference_x - row1.Reference_x)/d)
                        temp2Y = row1.Reference_y + row1.Euclidean_Dist * ((row2.Reference_y - row1.Reference_y)/d)
                        data1 = {
                            'New_Lat': temp1X,
                            'New_Lon': temp1Y
                        }
                        data2 = {
                            'New_Lat': temp2X,
                            'New_Lon': temp2Y
                        }
                        final.append(data1)
                        final.append(data2)
                    elif d > abs(row2.Euclidean_Dist - row1.Euclidean_Dist):
                        #Unsure of this formula, pulled it from online, needs testing
                        print("Circles meet at exactly 2 points!")
                        centerDist = ((row1.Euclidean_Dist**2 - row2.Euclidean_Dist**2 + d**2)/(2.0 * d))
                        centerX = row1.Reference_x + (dx * (centerDist/d))
                        centerY = row1.Reference_y + (dy * (centerDist/d))
                        height = math.sqrt(row2.Euclidean_Dist**2 - centerDist**2)
                        temp1X = centerX + (-1) * dy * (height/d)
                        temp1Y = centerY + dx * (height/d)
                        temp2X = centerX - (-1) * dy * (height/d)
                        temp2Y = centerY - dx * (height/d)
                        data1 = {
                            'New_Lat': temp1X,
                            'New_Lon': temp1Y
                        }
                        data2 = {
                            'New_Lat': temp2X,
                            'New_Lon': temp2Y
                        }
                        final.append(data1)
                        final.append(data2)
                    else:
                        print("Error! One circle is completely inside another.  Cannot perform calculation!")
                        return
            finaldf = pd.DataFrame(final, columns=['New_Lat','New_Lon'])
            print(finaldf)
            self.newLoc = Point(round(finaldf["New_Lat"].mean(), 6), round(finaldf["New_Lon"].mean(), 6))
            return
        else:
            df = pd.DataFrame(self.traceData, columns=['Reference', 'DX', 'DY', 'Distance_PX', 'Distance_Actual', 'Bearing', 'New_Lat', 'New_Lon', 'Units'])
            df[['Reference_x', 'Reference_y']] = pd.DataFrame(df['Reference'].tolist(), index=df.index)
            df.drop('Reference', axis=1, inplace=True)
            df = df[['Reference_x', 'Reference_y', 'DX', 'DY', 'Distance_PX', 'Distance_Actual', 'Bearing', 'New_Lat', 'New_Lon', 'Units']]
            #print(df)
            self.newLoc = Point(round(df["New_Lat"].mean(), 6), round(df["New_Lon"].mean(), 6))
            return
    
    def convertEuclidean(self, refx, refy, endx, endy):
        '''
        Convert reference point (lat, long) and new point (lat, long) to euclidian distance in (lat, long)
        '''
        actualx = endx - refx
        actualy = endy - refy
        return round(np.sqrt(actualx**2 + actualy**2), 6)

    def resetTrace(self):
        '''
        Reset reference points if user needs to trace again
        '''
        self.refIter = iter(self.ref)
        self.currentRef = next(self.refIter)
        self.traceData = []
        self.zeroVariables()
        self.updateLabel()

    def updateLabel(self):
        '''
        Constantly update data on window label
        '''
        dx = self.dx + self.temp_dx
        dy = self.dy + self.temp_dy
        distpx = self.dist_px
        ref = self.currentRef
        bearing = self.bearing
        dist = self.dist
        new_loc = (self.newLoc.x, self.newLoc.y)

        self.displayBox.update(
            dx,
            dy,
            distpx,
            ref,
            bearing,
            dist,
            new_loc
        )
    
    def update(self):
        '''
        Tracks current x and y distance and updates label
        '''
        geo = self.geometry()
        cur = self.cursor
        center = self.getCenter()
        
        #Get current x, y, and straight line distance from center
        self.temp_dx = self.getDX()
        self.temp_dy = self.getDY()
        self.dist_px = self.getDistance(self.dx + self.temp_dx, self.dy + self.temp_dy)

        self.bearing = self.getBearing(self.dx + self.temp_dx, self.dy + self.temp_dy)
        self.dist = self.convert(self.dist_px, self.scale)
        self.newLoc = self.newLocation(self.currentRef, self.dist, self.bearing)
            
        #Check if cursor is within window boundaries
        #Only update dx, dy instance variables when border has been reached
        curLoc = {cur.pos().x(), cur.pos().y()}
        boundaries = {0, geo.width()-1, geo.height()-1}

        if curLoc.intersection(boundaries):
            self.dx += self.temp_dx
            self.dy += self.temp_dy
            cur.setPos(center.x, center.y)

        self.updateLabel()

class ScaleDisplayWidget(QWidget):
    def __init__(self, parent=None):
        super(ScaleDisplayWidget, self).__init__(parent)
        self.setFixedSize(280, 150)
        self.initUI()
        self.update(0, 0, 0)

    def initUI(self):
        '''
        Setup GUI elements of scale window
        '''
        mainLayout = QGridLayout()

        self.dx_label = QLabel('DX (px):')
        self.dx_label.setFixedWidth(105)
        self.dx_edit = QLineEdit()
        self.dx_edit.setReadOnly(True)
        self.dx_edit.setFixedWidth(150)

        self.dy_label = QLabel('DY (px):')
        self.dy_label.setFixedWidth(105)
        self.dy_edit = QLineEdit()
        self.dy_edit.setReadOnly(True)
        self.dy_edit.setFixedWidth(150)

        self.dist_label = QLabel('Distance (px):')
        self.dist_label.setFixedWidth(105)
        self.dist_edit = QLineEdit()
        self.dist_edit.setReadOnly(True)
        self.dist_edit.setFixedWidth(150)

        mainLayout.addWidget(self.dx_label, 0, 0, Qt.AlignLeft)
        mainLayout.addWidget(self.dx_edit, 0, 1, Qt.AlignLeft)
        mainLayout.addWidget(self.dy_label, 1, 0, Qt.AlignLeft)
        mainLayout.addWidget(self.dy_edit, 1, 1, Qt.AlignLeft)
        mainLayout.addWidget(self.dist_label, 2, 0, Qt.AlignLeft)
        mainLayout.addWidget(self.dist_edit, 2, 1, Qt.AlignLeft)
    
        self.setLayout(mainLayout)

    def update(self, dx, dy, dist):
        self.dx_edit.setText(str(dx))
        self.dy_edit.setText(str(dy))
        self.dist_edit.setText(str(dist))

class LocationDisplayWidget(QWidget):
    def __init__(self, units, parent=None):
        super(LocationDisplayWidget, self).__init__(parent)
        self.units = units
        self.setFixedSize(350, 300)
        self.initUI()
        self.update(0, 0, 0, (0, 0), 0, 0, (0, 0))

    def initUI(self):
        '''
        Setup GUI elements of scale window
        '''
        mainLayout = QGridLayout()

        self.dx_label = QLabel('DX (px):')
        self.dx_label.setFixedWidth(125)
        self.dx_edit = QLineEdit()
        self.dx_edit.setReadOnly(True)
        self.dx_edit.setFixedWidth(200)

        self.dy_label = QLabel('DY (px):')
        self.dy_label.setFixedWidth(125)
        self.dy_edit = QLineEdit()
        self.dy_edit.setReadOnly(True)
        self.dy_edit.setFixedWidth(200)

        self.dist_label = QLabel('Distance (px):')
        self.dist_label.setFixedWidth(125)
        self.dist_edit = QLineEdit()
        self.dist_edit.setReadOnly(True)
        self.dist_edit.setFixedWidth(200)

        self.ref_label = QLabel('Reference:')
        self.ref_label.setFixedWidth(125)
        self.ref_edit = QLineEdit()
        self.ref_edit.setReadOnly(True)
        self.ref_edit.setFixedWidth(200)

        self.bear_label = QLabel('Bearing (deg):')
        self.bear_label.setFixedWidth(125)
        self.bear_edit = QLineEdit()
        self.bear_edit.setReadOnly(True)
        self.bear_edit.setFixedWidth(200)

        self.dist2_label = QLabel(f'Distance ({self.units}):')
        self.dist2_label.setFixedWidth(125)
        self.dist2_edit = QLineEdit()
        self.dist2_edit.setReadOnly(True)
        self.dist2_edit.setFixedWidth(200)

        self.new_label = QLabel('Location:')
        self.new_label.setFixedWidth(125)
        self.new_edit = QLineEdit()
        self.new_edit.setReadOnly(True)
        self.new_edit.setFixedWidth(200)

        mainLayout.addWidget(self.dx_label, 0, 0, Qt.AlignLeft)
        mainLayout.addWidget(self.dx_edit, 0, 1, Qt.AlignLeft)
        mainLayout.addWidget(self.dy_label, 1, 0, Qt.AlignLeft)
        mainLayout.addWidget(self.dy_edit, 1, 1, Qt.AlignLeft)
        mainLayout.addWidget(self.dist_label, 2, 0, Qt.AlignLeft)
        mainLayout.addWidget(self.dist_edit, 2, 1, Qt.AlignLeft)
        mainLayout.addWidget(self.ref_label, 3, 0, Qt.AlignLeft)
        mainLayout.addWidget(self.ref_edit, 3, 1, Qt.AlignLeft)
        mainLayout.addWidget(self.bear_label, 4, 0, Qt.AlignLeft)
        mainLayout.addWidget(self.bear_edit, 4, 1, Qt.AlignLeft)
        mainLayout.addWidget(self.dist2_label, 5, 0, Qt.AlignLeft)
        mainLayout.addWidget(self.dist2_edit, 5, 1, Qt.AlignLeft)
        mainLayout.addWidget(self.new_label, 6, 0, Qt.AlignLeft)
        mainLayout.addWidget(self.new_edit, 6, 1, Qt.AlignLeft)
    
        self.setLayout(mainLayout)

    def update(self, dx, dy, dist, ref, bearing, dist_unit, new_loc):
        self.dx_edit.setText(str(dx))
        self.dy_edit.setText(str(dy))
        self.dist_edit.setText(str(dist))
        self.ref_edit.setText(str(ref))
        self.bear_edit.setText(str(bearing))
        self.dist2_edit.setText(str(dist_unit))
        self.new_edit.setText(str(new_loc))