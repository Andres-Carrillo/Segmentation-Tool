from PyQt5.QtWidgets import (QWidget)
from PyQt5 import QtWidgets
from PyQt5 import QtCore
from PyQt5.QtGui import QPainter, QPen, QColor, QBrush
from utils import calculate_angle_between,calculate_poin_along_arc,in_circle


class Gauge(QWidget):
    def __init__(self, parent = None, kernel_size=5, iterations=1, background_color=QColor(217, 217, 206), handle_color=QColor(255, 255, 255), outline_color=QColor(0, 0, 0)):
        super().__init__(parent)
        self.kernel_size = kernel_size
        self.iterations = iterations
        self.max = 7
        self.min = 1

        self.background_color = background_color
        self.handle_color = handle_color
        self.outline_color = outline_color
        self.dragging = False
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

            if (angle < 1 or angle > 178) and self.dragging:
            
                point = calculate_poin_along_arc((center.x(),center.y()), int(self.handle_track.width()/2),angle)

                self.handle_center = QtCore.QPoint(point[0], point[1])

                self.update()