from PyQt5.QtWidgets import (QWidget)
from PyQt5 import QtWidgets
from PyQt5 import QtCore
from PyQt5.QtGui import QPainter, QPen, QColor, QBrush
from utils import calculate_angle_between,calculate_point_along_arc,in_circle


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
        self.title = None

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

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # draw background of the dial
        painter.setPen(QPen(self.background_color, 20))
        painter.drawArc(self.handle_track, 0, 180 * 16)
        
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
        # print("value in int",self.current_value)
        # print("the current value",str(self.current_value))
        painter.drawText(value_rect, QtCore.Qt.AlignmentFlag.AlignCenter, str(self.current_value))

        # draw the title
        if self.title is not None:
             font = painter.font()
            #  font.setPointSize(20)
            #  painter.setFont(font)
            #  painter.setPen(QPen(self.outline_color, 2))

            #  print("self.rect()",self.rect())
            #  print("inner_ring",self.inner_ring)
            #  print("outer_ring",self.outer_ring.getRect())
             title_rect = QtCore.QRectF(int(self.outer_ring.x()), int(self.inner_ring.y() + self.inner_ring.height()/2), 120, 40)
            #  title_rect.setX(int(self.handle_center.x()))
            #  title_rect.setY(int(self.handle_center.y() - 20))
             painter.drawText(title_rect, QtCore.Qt.AlignmentFlag.AlignCenter, self.title)

        painter.end()
        
    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.MouseButton.LeftButton:
                clicked_handle = in_circle(self.handle_center.x(),self.handle_center.y(), event.pos().x(), event.pos().y(), self.handle_size)
                
                if clicked_handle:
                    self.dragging = True
              
    def mouseReleaseEvent(self, event):
        if event.button() == QtCore.Qt.MouseButton.LeftButton:
            self.dragging = False
        
    def mouseMoveEvent(self, event):
            center = self.handle_track.center()
            angle = calculate_angle_between((center.x(),center.y()), (event.pos().x(), event.pos().y()))
            print("angle",angle)

            if self.dragging:
                point = calculate_point_along_arc((center.x(),center.y()), int(self.handle_track.width()/2),angle)


                end_point = calculate_point_along_arc((center.x(),center.y()), int(self.handle_track.width()/2),0)
                
                end_angle = calculate_angle_between((center.x(),center.y()), (end_point[0], end_point[1]))
                
                # need to test calulating angle based on starting point of the arc
                end_angle = calculate_angle_between((event.pos()[0],center.pos().y()), (self.start_cap.x(), self.start_cap.y()))
                # print("end point",end_point)
                print("end angle",end_angle)
                
                start_point = calculate_point_along_arc((center.x(),center.y()), int(self.handle_track.width()/2),179)

               
                # base case the angle is within the expected range
                if (angle < 1 or angle > 178):
                    self.handle_center = QtCore.QPoint(point[0], point[1])

                    #percentage should be angle based

                    percent = (point[0] - start_point[0]) / (end_point[0] - start_point[0]) 
       
                    self.current_value = int(percent * self.max)
                # edge case the angle is outside the expected range and would result in a value larger than the max
                elif angle > 1 and angle < 45:
                    self.current_value = self.max
                   

            self.update()


    def set_title(self, title:str):
        """
        Set the title of the gauge
        :param title: str
        :return: None
        """
        self.title = title
        self.update()