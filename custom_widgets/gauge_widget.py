from PyQt5.QtWidgets import (QWidget)
from PyQt5 import QtWidgets
from PyQt5 import QtCore
from PyQt5.QtGui import QPainter, QPen, QColor, QBrush
from utils import calculate_angle_between,calculate_point_along_arc,in_circle,convert_angle_to_360,convert_angle_to_counter_clockwise


class Gauge(QWidget):
    def __init__(self, parent = None, min=0, max=255, background_color=QColor(217, 217, 206), handle_color=QColor(255, 255, 255), outline_color=QColor(0, 0, 0)):
        super().__init__(parent)
    
        self.min = min
        self.max = max
        self.current_value = 0

        self.background_color = background_color
        self.handle_color = handle_color
        self.outline_color = outline_color
        self.dragging = False
        self.keyboard_control = False
        self.title = None
        self.mouse_position = None

        self.setMouseTracking(True)
        self.setSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        
        self.setMinimumSize(200, 200)
        self.setStyleSheet("background-color: None;")

        # rectangles used to draw the inner and outer edges of the dial
        self.inner_ring = self.rect().adjusted(20, 20, -20, -20)
        self.outer_ring = self.rect().adjusted(40, 40, -40, -40)
        self.handle_track = self.rect().adjusted(30, 30, -30, -30)
        
        # rectangles used to draw the endcaps of the dial
        self.start_cap = QtCore.QRectF(20, 90, 20, 20)
        self.end_cap = QtCore.QRectF(160, 90, 20, 20)

        self.handle_center = self.start_cap.center()
        self.handle_size = 10

        self.setFocusPolicy(QtCore.Qt.FocusPolicy.StrongFocus)


    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # draw background of the dial
        painter.setPen(QPen(self.background_color, 20))
        painter.drawArc(self.handle_track, 0, 180 * 16)

        #draw the filled arc
        painter.setPen(QPen(self.outline_color, 18))
        painter.setBrush(QBrush(self.outline_color))

        current_angle = calculate_angle_between((self.handle_track.x(),self.handle_track.y()), (self.handle_center.x(),self.handle_center.y()))
        current_angle = convert_angle_to_360(current_angle)

        print(f"current angle: {current_angle }")
        painter.drawArc(self.handle_track, 0, int(abs(current_angle - 180)) * 16)
        
        # set painter color and brush for the inner and outer arcs
        painter.setPen(QPen(self.outline_color, 2))      

        # draw the outline of the dial
        painter.drawArc(self.inner_ring, 0, 180 * 16)
        painter.drawArc(self.outer_ring, 0, 180 * 16)

        # draw the endcaps of each arc
        painter.drawArc(self.start_cap, 0, -180 * 16)
        painter.drawArc(self.end_cap, 0, -180 * 16)

        # draw the handle
        painter.setBrush(QBrush(self.handle_color))
        painter.drawEllipse(self.handle_center,self.handle_size, self.handle_size)
        
        # DRAW THE CURRENT VALUE
        painter.setPen(QPen(self.outline_color, 2))
        font = painter.font()
        font.setPointSize(20)
        painter.setFont(font)

        value_rect = QtCore.QRectF(int(self.outer_ring.x()), int(self.outer_ring.y() + self.inner_ring.height()/6), 120, 40)

        painter.drawText(value_rect, QtCore.Qt.AlignmentFlag.AlignCenter, str(self.current_value))

        # draw the title
        if self.title is not None:
             font = painter.font()
             title_rect = QtCore.QRectF(int(self.outer_ring.x()), int(self.inner_ring.y() + self.inner_ring.height()/2), 120, 40)
            
             painter.drawText(title_rect, QtCore.Qt.AlignmentFlag.AlignCenter, self.title)

        painter.end()
        
    def mousePressEvent(self, event):

        if event.button() == QtCore.Qt.MouseButton.LeftButton:
                clicked_handle = in_circle(self.handle_center.x(),self.handle_center.y(), event.pos().x(), event.pos().y(), self.handle_size)
                
                if clicked_handle:
                    self.dragging = True

        if event.button() == QtCore.Qt.MouseButton.RightButton:
            clicked_handle = in_circle(self.handle_center.x(),self.handle_center.y(), event.pos().x(), event.pos().y(), self.handle_size)
       
            if clicked_handle:
                self.keyboard_control = not self.keyboard_control
                self.setFocus()

              
    def mouseReleaseEvent(self, event):
        if event.button() == QtCore.Qt.MouseButton.LeftButton:
            self.dragging = False

        # if event.button() == QtCore.Qt.MouseButton.RightButton:
        #      self.keyboard_control = False
        
    def mouseMoveEvent(self, event):
            center = self.handle_track.center()
            angle = calculate_angle_between((center.x(),center.y()), (event.pos().x(), event.pos().y()))
            
            angle = convert_angle_to_360(angle)

            if self.dragging:
                self.mouse_position = event.pos()
                point = calculate_point_along_arc((center.x(),center.y()), int(self.handle_track.width()/2),angle)

                # base case the angle is within the expected range
                if (angle > 178 or (angle <5)):
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

                point = calculate_point_along_arc((self.handle_track.center().x(),self.handle_track.center().y()), int(self.handle_track.width()/2),angle)

                self.handle_center = QtCore.QPoint(point[0], point[1])

                self.update()


    def set_title(self, title:str):
        """
        Set the title of the gauge
        :param title: str
        :return: None
        """
        self.title = title
        self.update()