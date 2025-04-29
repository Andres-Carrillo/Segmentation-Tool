from PyQt5.QtWidgets import (QWidget)
from PyQt5 import QtWidgets
from PyQt5 import QtCore
from PyQt5.QtGui import QPainter, QPen, QColor, QBrush
from utils import calculate_angle_between,in_circle,convert_angle_to_360,calculate_point_along_ellipse
import numpy as np

class Gauge(QWidget):
    def __init__(self, parent = None, min=1, max=7, background_color=QColor(217, 217, 206), handle_color=QColor(255, 255, 255), outline_color=QColor(0, 0, 0)):
        super().__init__(parent)
    
        self.min = min
        self.max = max
        self.current_value = 0

        self.background_color = background_color
        self.handle_color = handle_color
        self.outline_color = outline_color
        self.dragging = False
        self.keyboard_control = False
        self.display_value = True
        self.title = None
        self.mouse_position = None

        self.setMouseTracking(True)
        self.setSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        self.setMinimumSize(100, 100)
        self.setStyleSheet("background-color: None;")
        
        self.handle_size = 10

        self.setFocusPolicy(QtCore.Qt.FocusPolicy.StrongFocus)

    def resizeEvent(self, event):
        # Update the inner, outer, and handle track rectangles based on the widget's geometry
        self.inner_ring = self.rect().adjusted(20, 20, -20, -20)
        self.outer_ring = self.rect().adjusted(40, 40, -40, -40)
        self.handle_track = self.rect().adjusted(30, 30, -30, -30)

        # Update the start and end caps
        self.start_cap = QtCore.QRectF(self.inner_ring.bottomLeft().x(), self.inner_ring.bottomLeft().y() / 2, 20, 20)
        self.end_cap = QtCore.QRectF(self.outer_ring.bottomRight().x() + 1, self.inner_ring.bottomLeft().y() / 2, 20, 20)

        # Update the handle position to start at the start cap
        self.handle_center = self.start_cap.center()

        # Call the parent class's resizeEvent
        super().resizeEvent(event)
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(QPen(self.outline_color, 2))
        painter.setBrush(QBrush(self.outline_color))

        # draw background of the dial
        painter.setPen(QPen(self.background_color, 15))
        painter.drawArc(self.handle_track, 0, 180 * 16)

        # draw the filled arc
        painter.setBrush(QBrush(self.outline_color))
        
        # # #draw the progress bar of the gauge
        # current_angle = calculate_angle_between((self.end_cap.center().x(),self.end_cap.center().y()), (self.handle_center.x(),self.handle_center.y())) 
        # current_angle = int(self._calc_progress_bar_distance() )        
        # current_angle = 0 if current_angle < 0 else -current_angle
        # painter.drawArc(self.handle_track, 180*16, current_angle * 16)

        # set painter color and brush for the inner and outer arcs
        painter.setPen(QPen(self.outline_color, 2))      

        # draw the outline of the dial
        painter.drawArc(self.inner_ring, 0, 180 * 16)
        painter.drawArc(self.outer_ring, 0, 180 * 16)

        # # draw the endcaps of each arc
        painter.drawArc(self.start_cap, 0, -180 * 16)
        painter.drawArc(self.end_cap, 0, -180 * 16)

        # draw the handle
        painter.setBrush(QBrush(self.handle_color))
        painter.drawEllipse(self.handle_center,self.handle_size, self.handle_size)
        
        # DRAW THE CURRENT VALUE
        if self.display_value:
            font = painter.font()
            font.setPointSize(int(self.rect().height()/18))
            painter.setFont(font)

            text_rect = QtCore.QRectF(int(self.rect().x() + self.rect().width()/4), int(self.outer_ring.y() + self.inner_ring.height()/6), self.rect().width()/2, self.rect().height()/4)
            painter.drawText(text_rect, QtCore.Qt.AlignmentFlag.AlignCenter, str(self.current_value))

        # draw the title
        if self.title is not None:
             font = painter.font()
             font.setPointSize(int(self.rect().height()/18))
             painter.setFont(font)

             text_rect = QtCore.QRectF(int(self.rect().x() + self.rect().width()/4), int(self.inner_ring.y() + self.inner_ring.height()/2), self.rect().width()/2, self.rect().height()/4)
             painter.drawText(text_rect, QtCore.Qt.AlignmentFlag.AlignCenter, self.title)

        painter.end()
        
    def mousePressEvent(self, event):

        if event.button() == QtCore.Qt.MouseButton.LeftButton:
                
                clicked_handle = in_circle(self.handle_center.x(),self.handle_center.y(), event.pos().x(), event.pos().y(), self.handle_size)
                if clicked_handle:
                    self.dragging = True

        if event.button() == QtCore.Qt.MouseButton.RightButton:
            clicked_handle = in_circle(self.handle_center.x(),self.handle_center.y(), event.pos().x(), event.pos().y(), self.handle_size)
       
          
        self.keyboard_control = not self.keyboard_control
        self.setFocus()

              
    def mouseReleaseEvent(self, event):
        if event.button() == QtCore.Qt.MouseButton.LeftButton:
            self.dragging = False
        
    def mouseMoveEvent(self, event):
            center = self.handle_track.center()
            angle = calculate_angle_between((center.x(),center.y()), (event.pos().x(), event.pos().y()))
            angle = convert_angle_to_360(angle)

            if self.dragging:
                point = self._calc_position_of_handle(angle)
                self.mouse_position = event.pos()

                # base case the angle is within the expected range
                if (angle > 178 or (angle <2)):
                    # set new handle position
                    self.handle_center = QtCore.QPoint(point[0], point[1])

                    # calculate the max angle based on the center of gauge and the end cap
                    max_angle = calculate_angle_between((center.x(),center.y()), (self.end_cap.x(), self.end_cap.y()))
                    max_angle = convert_angle_to_360(max_angle)

                    #starting angle of the arc
                    min_angle = 178

                    percent = abs((angle - min_angle) / (max_angle - min_angle))

                    #clamp the percent between 0 and 1
                    percent = max(min(percent, 1),0)
       
                    self.current_value = int(percent * self.max)
                # edge case the angle is outside the expected range and would result in a value larger than the max
                elif angle > 120 and self.current_value < self.max - 10:
                    self.current_value = self.min
                    self.handle_center = self.start_cap.center()

                elif angle < 85 and self.current_value > self.min + 30:
                    self.current_value = self.max
                    self.handle_center = self.end_cap.center()   

            self.update()


    def keyPressEvent(self, event):
            key = event.key()

            if self.keyboard_control:
                if key == QtCore.Qt.Key.Key_Down:
                    self.current_value -= 1
                elif key == QtCore.Qt.Key.Key_Up:
                    self.current_value += 1

                # clamp the value between min and max
                self.current_value = max(self.min, min(self.max, self.current_value))

                # update the handle position based on the current value
                percent = (self.current_value - self.min) / (self.max - self.min)
                angle = 178 + percent * (360 - 178)

                point = self._calc_position_of_handle(angle) #calculate_point_along_arc((self.handle_track.center().x(),self.handle_track.center().y()), int(self.handle_track.width()/2),angle)

                self.handle_center = QtCore.QPoint(point[0], point[1])

                self.update()

    def _calc_position_of_handle(self,angle):
            center = self.handle_track.center()
                     # Calculate the radii of the ellipse
            radius_x = self.handle_track.width() / 2  # Horizontal radius
            radius_y = self.handle_track.height() / 2  # Vertical radius

                # Calculate the handle position along the elliptical curve
            point = calculate_point_along_ellipse((center.x(), center.y()), radius_x, radius_y, angle)

            return point
         
    def set_title(self, title:str):
        """
        Set the title of the gauge
        :param title: str
        :return: None
        """
        self.title = title
        self.update()


    def _calc_progress_bar_distance(self):
        center = self.handle_track.center()

        # Calculate the radii of the ellipse
        radius_x = self.handle_track.width() / 2  # Horizontal radius
        radius_y = self.handle_track.height() / 2  # Vertical radius

        # Define a helper function to calculate the elliptical arc length
        def elliptical_arc_length(start_angle, end_angle, radius_x, radius_y, num_segments=100):
            angles = np.linspace(np.radians(start_angle), np.radians(end_angle), num_segments)
            dx = radius_x * np.cos(angles)
            dy = radius_y * np.sin(angles)
            distances = np.sqrt(np.diff(dx)**2 + np.diff(dy)**2)
            return np.sum(distances)

        # Calculate the total arc length of the elliptical segment
        min_angle = 178
        max_angle = calculate_angle_between((center.x(), center.y()), (self.end_cap.x(), self.end_cap.y()))
        max_angle = convert_angle_to_360(max_angle)
        total_arc_length = elliptical_arc_length(min_angle, max_angle, radius_x, radius_y)

        # Calculate the arc length from min_angle to the handle's current position
        angle = calculate_angle_between((center.x(), center.y()), (self.handle_center.x(), self.handle_center.y()))
        angle = convert_angle_to_360(angle)
        current_arc_length = elliptical_arc_length(min_angle, angle, radius_x, radius_y)

        # Calculate the percentage of the arc traversed
        percent = current_arc_length / total_arc_length
        percent = max(min(percent, 1), 0)  # Clamp between 0 and 1

        # Adjust the progress bar span to match the elliptical geometry
        progress_span = percent * (max_angle - min_angle)

        return progress_span